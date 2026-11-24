"""
Kubernetes manifest extractor for reverse engineering.

Extracts architectural resources from Kubernetes YAML manifests:
- Deployments, Pods, StatefulSets → resources
- Services → interfaces
- ConfigMaps, Secrets → metadata
- Labels → tags
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any

from ..model import Resource, Interface
from . import Extractor, ExtractionError


class KubernetesExtractor(Extractor):
    """Extract architectural resources from Kubernetes manifests."""

    # Kubernetes resource kinds we extract
    SUPPORTED_KINDS = {'Deployment', 'Pod', 'StatefulSet', 'DaemonSet', 'Service'}

    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a Kubernetes manifest.

        Args:
            file_path: Path to check

        Returns:
            True if file is a Kubernetes YAML with apiVersion and kind
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        if file_path.suffix not in ['.yaml', '.yml']:
            return False

        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)

            # Check for Kubernetes manifest markers
            if isinstance(data, dict):
                return 'apiVersion' in data and 'kind' in data
            return False

        except (yaml.YAMLError, IOError, UnicodeDecodeError):
            return False

    def extract(self, file_path: Path) -> List[Resource]:
        """Extract resources from Kubernetes manifest.

        Args:
            file_path: Path to manifest file

        Returns:
            List of Resources extracted from the manifest

        Raises:
            ExtractionError: If extraction fails
        """
        try:
            with open(file_path, 'r') as f:
                # Support both single document and multi-document YAML
                docs = list(yaml.safe_load_all(f))

            resources = []
            for doc in docs:
                if not isinstance(doc, dict):
                    continue

                kind = doc.get('kind')
                if kind in self.SUPPORTED_KINDS:
                    resource = self._extract_resource(doc, file_path)
                    if resource:
                        resources.append(resource)

            return resources

        except yaml.YAMLError as e:
            raise ExtractionError(
                f"Failed to parse Kubernetes YAML: {e}",
                file_path=file_path
            )
        except Exception as e:
            raise ExtractionError(
                f"Failed to extract from Kubernetes manifest: {e}",
                file_path=file_path
            )

    def _extract_resource(self, manifest: Dict[str, Any], file_path: Path) -> Resource:
        """Extract a single Kubernetes resource.

        Args:
            manifest: Kubernetes manifest dictionary
            file_path: Path to manifest file

        Returns:
            Resource representing the Kubernetes object
        """
        kind = manifest.get('kind')
        metadata = manifest.get('metadata', {})
        spec = manifest.get('spec', {})

        # Get name and namespace
        name = metadata.get('name', 'unknown')
        namespace = metadata.get('namespace', 'default')

        # Generate resource ID
        resource_id = f"{name.replace('_', '-')}"

        # Extract labels as tags
        labels = metadata.get('labels', {})
        tags = ['kubernetes', kind.lower()] + [f"{k}:{v}" for k, v in labels.items()]

        # Build interfaces based on kind
        interfaces = []
        if kind == 'Service':
            interfaces = self._extract_service_interfaces(spec)
        elif kind in ['Deployment', 'StatefulSet']:
            # Check for container ports
            template = spec.get('template', {})
            containers = template.get('spec', {}).get('containers', [])
            for container in containers:
                for port in container.get('ports', []):
                    port_num = port.get('containerPort')
                    port_name = port.get('name', f"port-{port_num}")
                    interface = Interface(
                        id=port_name.replace('_', '-'),
                        protocol='http' if port_num in [80, 8080, 443] else 'tcp',
                        direction='request-response',
                        description=f"Container port {port_num}",
                        metadata={'port': str(port_num)}
                    )
                    interfaces.append(interface)

        # Determine technology from container images
        technology = self._extract_technology(spec, kind)

        # Build metadata
        resource_metadata = {
            'kind': kind,
            'namespace': namespace,
            'manifest': str(file_path)
        }
        if labels:
            resource_metadata['labels'] = labels

        # Create resource
        resource = Resource(
            id=resource_id,
            name=name.replace('-', ' ').replace('_', ' ').title(),
            type=f"k8s-{kind.lower()}",
            technology=technology,
            description=f"Kubernetes {kind}: {name}",
            repository=str(file_path),
            interfaces=interfaces,
            metadata=resource_metadata,
            tags=tags
        )

        return resource

    def _extract_service_interfaces(self, spec: Dict[str, Any]) -> List[Interface]:
        """Extract interfaces from a Kubernetes Service.

        Args:
            spec: Service spec section

        Returns:
            List of Interface objects
        """
        interfaces = []
        ports = spec.get('ports', [])

        for port_config in ports:
            port = port_config.get('port')
            target_port = port_config.get('targetPort', port)
            port_name = port_config.get('name', f"port-{port}")
            protocol = port_config.get('protocol', 'TCP').lower()

            interface = Interface(
                id=port_name.replace('_', '-'),
                protocol='http' if port in [80, 8080, 443] else protocol.lower(),
                direction='request-response',
                description=f"Service port {port} → {target_port}",
                metadata={
                    'port': str(port),
                    'targetPort': str(target_port),
                    'protocol': protocol
                }
            )
            interfaces.append(interface)

        return interfaces

    def _extract_technology(self, spec: Dict[str, Any], kind: str) -> str:
        """Extract technology from container images.

        Args:
            spec: Resource spec section
            kind: Resource kind

        Returns:
            Technology string
        """
        if kind in ['Deployment', 'StatefulSet', 'DaemonSet']:
            template = spec.get('template', {})
            containers = template.get('spec', {}).get('containers', [])
            if containers:
                image = containers[0].get('image', '')
                # Extract base image name
                base = image.split(':')[0].split('/')[-1]
                return base.title()

        return 'Kubernetes'
