"use client"

import { useEffect, useRef } from "react"
import katex from "katex"

interface LatexProps {
  children: string
  display?: boolean
  className?: string
}

export function Latex({ children, display = false, className = "" }: LatexProps) {
  const ref = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (ref.current && children) {
      try {
        katex.render(children, ref.current, {
          displayMode: display,
          throwOnError: false,
          trust: true,
        })
      } catch (e) {
        ref.current.textContent = children
      }
    }
  }, [children, display])

  return <span ref={ref} className={className} />
}

export function renderLatex(text: string): (string | { latex: string; display: boolean })[] {
  if (!text) return [text]

  const parts: (string | { latex: string; display: boolean })[] = []
  let remaining = text
  let key = 0

  const displayRegex = /\$\$([^$]+)\$\$|\\\[([^\]]+)\\\]/g
  const inlineRegex = /\$([^$]+)\$|\\\(([^)]+)\\\)/g

  let match: RegExpExecArray | null

  remaining = remaining.replace(/\*\*(.+?)\*\*/g, "**$1**")

  const combinedRegex = /(\$\$[^$]+\$\$|\\\[[^\]]+\\\]|\$[^$]+\$|\\\([^)]+\\\))/g
  let lastIdx = 0

  while ((match = combinedRegex.exec(remaining)) !== null) {
    if (match.index > lastIdx) {
      parts.push(remaining.slice(lastIdx, match.index))
    }
    const m = match[0]
    const isDisplay = m.startsWith("$$") || m.startsWith("\\[")
    let formula = m
      .replace(/^\$\$/, "").replace(/\$\$$/, "")
      .replace(/^\\\[/, "").replace(/\\\]$/, "")
      .replace(/^\$/, "").replace(/\$$/, "")
      .replace(/^\\\(/, "").replace(/\\\)$/, "")
    parts.push({ latex: formula, display: isDisplay })
    lastIdx = combinedRegex.lastIndex
    key++
  }

  if (lastIdx < remaining.length) {
    parts.push(remaining.slice(lastIdx))
  }

  return parts.length > 0 ? parts : [text]
}

export function MixedText({ text, className = "" }: { text: string; className?: string }) {
  const parts = renderLatex(text)

  return (
    <span className={className}>
      {parts.map((part, i) =>
        typeof part === "string" ? (
          <span key={i}>{part}</span>
        ) : (
          <Latex key={i} display={part.display}>
            {part.latex}
          </Latex>
        )
      )}
    </span>
  )
}
