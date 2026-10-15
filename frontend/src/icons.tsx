import type { CSSProperties, SVGProps } from 'react'

type IconProps = {
  name: 'user' | 'info' | 'alert' | 'refresh' | 'zap' | 'chevron-right'
  size?: number
  color?: string
  sw?: number
  style?: CSSProperties
  className?: string
}

const Icon = ({ name, size = 20, color = 'currentColor', sw = 1.7, style, className }: IconProps) => {
  const p: SVGProps<SVGSVGElement> = {
    width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: color,
    strokeWidth: sw, strokeLinecap: 'round', strokeLinejoin: 'round', style, className, 'aria-hidden': true, focusable: false,
  }
  switch (name) {
    case 'chevron-right': return <svg {...p}><path d="M9 6l6 6-6 6" /></svg>
    case 'alert': return <svg {...p}><path d="M12 3.5l9.5 16.5H2.5L12 3.5z" /><path d="M12 9.5v4.5" /><circle cx="12" cy="17.5" r=".6" fill={color} /></svg>
    case 'info': return <svg {...p}><circle cx="12" cy="12" r="9" /><path d="M12 11v5" /><circle cx="12" cy="7.8" r=".6" fill={color} /></svg>
    case 'zap': return <svg {...p}><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z" /></svg>
    case 'user': return <svg {...p}><circle cx="12" cy="8" r="4" /><path d="M4 20c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5" /></svg>
    case 'refresh': return <svg {...p}><path d="M3 12a9 9 0 0115.5-6.2L21 8M21 4v4h-4M21 12a9 9 0 01-15.5 6.2L3 16M3 20v-4h4" /></svg>
    default: return <svg {...p}><circle cx="12" cy="12" r="9" /></svg>
  }
}

export default Icon
