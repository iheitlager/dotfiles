-- Context-aware Unicode → LaTeX rewriter.
-- Processes only Str nodes, so Code/CodeBlock/RawInline are left untouched.
-- Active for latex output format only (covers pdf-via-xelatex).

local map = {
  -- Arrows
  ["→"] = [[\ensuremath{\rightarrow}]],
  ["←"] = [[\ensuremath{\leftarrow}]],
  ["↑"] = [[\ensuremath{\uparrow}]],
  ["↓"] = [[\ensuremath{\downarrow}]],
  ["↔"] = [[\ensuremath{\leftrightarrow}]],
  ["⇒"] = [[\ensuremath{\Rightarrow}]],
  ["⇐"] = [[\ensuremath{\Leftarrow}]],
  ["⇔"] = [[\ensuremath{\Leftrightarrow}]],
  ["↦"] = [[\ensuremath{\mapsto}]],
  ["↩"] = [[\ensuremath{\hookleftarrow}]],
  ["↪"] = [[\ensuremath{\hookrightarrow}]],
  ["⟹"] = [[\ensuremath{\Longrightarrow}]],
  ["⟺"] = [[\ensuremath{\Longleftrightarrow}]],
  -- Math relations
  ["≤"] = [[\ensuremath{\leq}]],
  ["≥"] = [[\ensuremath{\geq}]],
  ["≠"] = [[\ensuremath{\neq}]],
  ["≈"] = [[\ensuremath{\approx}]],
  ["≡"] = [[\ensuremath{\equiv}]],
  ["∈"] = [[\ensuremath{\in}]],
  ["∉"] = [[\ensuremath{\notin}]],
  ["⊂"] = [[\ensuremath{\subset}]],
  ["⊃"] = [[\ensuremath{\supset}]],
  ["⊆"] = [[\ensuremath{\subseteq}]],
  ["⊇"] = [[\ensuremath{\supseteq}]],
  ["∩"] = [[\ensuremath{\cap}]],
  ["∪"] = [[\ensuremath{\cup}]],
  ["∀"] = [[\ensuremath{\forall}]],
  ["∃"] = [[\ensuremath{\exists}]],
  ["∄"] = [[\ensuremath{\nexists}]],
  -- Math operators
  ["∞"] = [[\ensuremath{\infty}]],
  ["∑"] = [[\ensuremath{\sum}]],
  ["∏"] = [[\ensuremath{\prod}]],
  ["√"] = [[\ensuremath{\sqrt{}}]],
  ["∂"] = [[\ensuremath{\partial}]],
  ["∇"] = [[\ensuremath{\nabla}]],
  ["∝"] = [[\ensuremath{\propto}]],
  ["±"] = [[\ensuremath{\pm}]],
  ["∓"] = [[\ensuremath{\mp}]],
  -- Typographic symbols
  ["×"] = [[\ensuremath{\times}]],
  ["÷"] = [[\ensuremath{\div}]],
  ["°"] = [[\ensuremath{{}^{\circ}}]],
  ["…"] = [[\ldots{}]],
  ["½"] = [[\ensuremath{\frac{1}{2}}]],
  ["¼"] = [[\ensuremath{\frac{1}{4}}]],
  ["¾"] = [[\ensuremath{\frac{3}{4}}]],
  ["™"] = [[\texttrademark{}]],
  ["©"] = [[\textcopyright{}]],
  ["®"] = [[\textregistered{}]],
  ["✓"] = [[\checkmark{}]],
  ["✗"] = [[\ensuremath{\times}]],
  ["•"] = [[\textbullet{}]],
  -- Dashes (fontspec handles these natively; included for pdflatex compat)
  ["–"] = [[\textendash{}]],
  ["—"] = [[\textemdash{}]],
}

local function rewrite(text)
  local parts = {}
  local buf = ""
  -- Iterate over UTF-8 codepoints byte by byte
  for char in text:gmatch("[%z\1-\127\194-\244][\128-\191]*") do
    local rep = map[char]
    if rep then
      if buf ~= "" then parts[#parts+1] = pandoc.Str(buf); buf = "" end
      parts[#parts+1] = pandoc.RawInline("latex", rep)
    else
      buf = buf .. char
    end
  end
  if buf ~= "" then parts[#parts+1] = pandoc.Str(buf) end
  return parts
end

function Str(el)
  if FORMAT ~= "latex" then return end
  local parts = rewrite(el.text)
  if #parts == 0 then return pandoc.Str("") end
  if #parts == 1 then return parts[1] end
  return parts
end
