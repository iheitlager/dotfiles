"""
Docker Compose extractor for reverse engineering.

Extracts architectural resources from docker-compose.yml files:
- Services → resources (type: docker-service)
- Volumes → metadata
- Networks → tags
- Environment variables → metadata
"""

import yaml
from pathlib import Path
from typing import List

from ..model import Resource, Interface
from . import Extractor, ExtractionError


class DockerExtractor(Extractor):
    """Extract architectural resources from docker-compose files."""

    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a docker-compose file.

        Args:
            file_path: Path to check

        Returns:
            True if file is docker-compose.yml or docker-compose.yaml
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        return file_path.name in ['docker-compose.yml', 'docker-compose.yaml']

    def extract(self, file_path: Path) -> List[Resource]:
        """Extract resources from docker-compose file.

        Args:
            file_path: Path to docker-compose.yml

        Returns:
            List of Resources (one per service)

        Raises:
            ExtractionError: If extraction fails
        """
        try:
            with open(file_path, 'r') as f:
                compose_data = yaml.safe_load(f)

            if not isinstance(compose_data, dict):
                raise ExtractionError(
                    "docker-compose file must be a dictionary",
                    file_path=file_path
                )

            resources = []
            services = compose_data.get('services', {})

            for service_name, service_config in services.items():
                resource = self._extract_service(service_name, service_config, file_path)
                resources.append(resource)

            return resources

        except yaml.YAMLError as e:
            raise ExtractionError(
                f"Failed to parse docker-compose YAML: {e}",
                file_path=file_path
            )
        except Exception as e:
            raise ExtractionError(
                f"Failed to extract from docker-compose: {e}",
                file_path=file_path
            )

    def _extract_service(self, service_name: str, config: dict, file_path: Path) -> Resource:
        """Extract a single service as a resource.

        Args:
            service_name: Name of the service
            config: Service configuration from compose file
            file_path: Path to compose file

        Returns:
            Resource representing the service
        """
        # Generate resource ID
        resource_id = service_name.replace('_', '-')

        # Extract image info
        image = config.get('image', 'unknown')
        technology = self._extract_technology(image)

        # Build interfaces from ports
        interfaces = []
        ports = config.get('ports', [])
        for port in ports:
            # Parse port mapping (e.g., "8080:80" or "80")
            if isinstance(port, str):
                parts = port.split(':')
                container_port = parts[-1].split('/')[0]  # Handle "80/tcp"
            else:
                container_port = str(port)

            interface = Interface(
                id=f"port-{container_port}",
                protocol='http' if container_port in ['80', '8080', '443'] else 'tcp',
                direction='request-response',
                description=f"Service port {container_port}",
                metadata={'port': container_port}
            )
            interfaces.append(interface)

        # Collect metadata
        metadata = {
            'image': image,
            'compose_file': str(file_path)
        }

        # Add environment variables
        env = config.get('environment', [])
        if env:
            metadata['environment'] = env

        # Add volumes
        volumes = config.get('volumes', [])
        if volumes:
            metadata['volumes'] = volumes

        # Create resource
        resource = Resource(
            id=resource_id,
            name=service_name.replace('_', ' ').replace('-', ' ').title(),
            type='docker-service',
            technology=technology,
            description=f"Docker service: {service_name}",
            repository=str(file_path),
            interfaces=interfaces,
            metadata=metadata,
            tags=['docker']
        )

        return resource

    def _extract_technology(self, image: str) -> str:
        """Extract technology from Docker image name.

        Args:
            image: Docker image (e.g., "postgres:15", "nginx:latest")

        Returns:
            Technology string (e.g., "PostgreSQL", "nginx")
        """
        # Get base image name before colon
        base = image.split(':')[0].split('/')[-1]

        # Map common images to tech names
        tech_map = {
            'postgres': 'PostgreSQL',
            'mysql': 'MySQL',
            'redis': 'Redis',
            'nginx': 'nginx',
            'node': 'Node.js',
            'python': 'Python',
            'golang': 'Go',
            'go': 'Go',
        }

        return tech_map.get(base.lower(), base.title())
