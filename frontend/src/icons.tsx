import type { CSSProperties, SVGProps } from 'react'

type IconProps = {
  name: string
  size?: number
  color?: string
  sw?: number
  style?: CSSProperties
  className?: string
}

const Icon = ({ name, size = 20, color = 'currentColor', sw = 1.7, style, className }: IconProps) => {
  const p: SVGProps<SVGSVGElement> = {
    width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: color,
    strokeWidth: sw, strokeLinecap: 'round', strokeLinejoin: 'round', style, className,
  }
  switch (name) {
    case 'grid': return <svg {...p}><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></svg>
    case 'columns': return <svg {...p}><rect x="3" y="4" width="5" height="16" rx="1.4" /><rect x="9.5" y="4" width="5" height="16" rx="1.4" /><rect x="16" y="4" width="5" height="16" rx="1.4" /></svg>
    case 'list': return <svg {...p}><path d="M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01" /></svg>
    case 'inbox': return <svg {...p}><path d="M22 12h-6l-2 3h-4l-2-3H2" /><path d="M5.5 5h13l3.5 7v6a1 1 0 01-1 1H3a1 1 0 01-1-1v-6l3.5-7z" /></svg>
    case 'folder': return <svg {...p}><path d="M3 7a2 2 0 012-2h4l2 2.5h8a2 2 0 012 2V18a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" /></svg>
    case 'layers': return <svg {...p}><path d="M12 2.5L21 7l-9 4.5L3 7l9-4.5z" /><path d="M3 12l9 4.5L21 12M3 17l9 4.5L21 17" /></svg>
    case 'settings': return <svg {...p}><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" /></svg>
    case 'search': return <svg {...p}><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.4-3.4" /></svg>
    case 'bell': return <svg {...p}><path d="M6 8a6 6 0 1112 0c0 4 1.6 5.2 2.2 6H3.8C4.4 13.2 6 12 6 8z" /><path d="M10 19a2 2 0 004 0" /></svg>
    case 'mail': return <svg {...p}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3.5 7l8.5 6 8.5-6" /></svg>
    case 'plus': return <svg {...p}><path d="M12 5v14M5 12h14" /></svg>
    case 'minus': return <svg {...p}><path d="M5 12h14" /></svg>
    case 'chevron-down': return <svg {...p}><path d="M6 9l6 6 6-6" /></svg>
    case 'chevron-right': return <svg {...p}><path d="M9 6l6 6-6 6" /></svg>
    case 'chevron-left': return <svg {...p}><path d="M15 6l-6 6 6 6" /></svg>
    case 'chevron-up': return <svg {...p}><path d="M6 15l6-6 6 6" /></svg>
    case 'arrow-right': return <svg {...p}><path d="M5 12h14M13 6l6 6-6 6" /></svg>
    case 'arrow-up-right': return <svg {...p}><path d="M7 17L17 7M8 7h9v9" /></svg>
    case 'check': return <svg {...p}><path d="M5 12.5l4.5 4.5L19 7" /></svg>
    case 'check-circle': return <svg {...p}><circle cx="12" cy="12" r="9" /><path d="M8.5 12l2.5 2.5 4.5-5" /></svg>
    case 'double-check': return <svg {...p}><path d="M2 12.5l4 4L13 9M11 16.5l1 .5L22 7" /></svg>
    case 'x': return <svg {...p}><path d="M6 6l12 12M18 6L6 18" /></svg>
    case 'x-circle': return <svg {...p}><circle cx="12" cy="12" r="9" /><path d="M9 9l6 6M15 9l-6 6" /></svg>
    case 'dots': return <svg {...p}><circle cx="5" cy="12" r="1.4" fill={color} stroke="none" /><circle cx="12" cy="12" r="1.4" fill={color} stroke="none" /><circle cx="19" cy="12" r="1.4" fill={color} stroke="none" /></svg>
    case 'dots-v': return <svg {...p}><circle cx="12" cy="5" r="1.4" fill={color} stroke="none" /><circle cx="12" cy="12" r="1.4" fill={color} stroke="none" /><circle cx="12" cy="19" r="1.4" fill={color} stroke="none" /></svg>
    case 'filter': return <svg {...p}><path d="M4 5h16l-6.4 8v5l-3.2 1.6V13L4 5z" /></svg>
    case 'sliders': return <svg {...p}><path d="M4 8h10M18 8h2M4 16h2M10 16h10" /><circle cx="16" cy="8" r="2.2" /><circle cx="8" cy="16" r="2.2" /></svg>
    case 'share': return <svg {...p}><circle cx="18" cy="5" r="2.6" /><circle cx="6" cy="12" r="2.6" /><circle cx="18" cy="19" r="2.6" /><path d="M8.3 10.8l7.4-4.3M8.3 13.2l7.4 4.3" /></svg>
    case 'link': return <svg {...p}><path d="M10 13a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1.5 1.5" /><path d="M14 11a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1.5-1.5" /></svg>
    case 'copy': return <svg {...p}><rect x="9" y="9" width="12" height="12" rx="2.4" /><path d="M5 15H4a1 1 0 01-1-1V4a1 1 0 011-1h10a1 1 0 011 1v1" /></svg>
    case 'eye': return <svg {...p}><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" /><circle cx="12" cy="12" r="3" /></svg>
    case 'eye-off': return <svg {...p}><path d="M3 3l18 18M10.6 6.2A9.9 9.9 0 0112 6c6.5 0 10 6 10 6a16.5 16.5 0 01-3.3 4.2M6.2 6.2A16.4 16.4 0 002 12s3.5 6 10 6a9.9 9.9 0 003.9-.8M9.9 9.9a3 3 0 004.2 4.2" /></svg>
    case 'paperclip': return <svg {...p}><path d="M21 11l-8.5 8.5a5 5 0 01-7-7L14 4a3.3 3.3 0 014.7 4.7l-9 9a1.7 1.7 0 01-2.4-2.4l8-8" /></svg>
    case 'image': return <svg {...p}><rect x="3" y="4" width="18" height="16" rx="2.4" /><circle cx="8.5" cy="9.5" r="1.8" /><path d="M21 16l-5-5-7 7" /></svg>
    case 'video': return <svg {...p}><rect x="2.5" y="6" width="13" height="12" rx="2.4" /><path d="M15.5 10.2l5-2.7v9l-5-2.7" /></svg>
    case 'play': return <svg {...p}><circle cx="12" cy="12" r="9" /><path d="M10 8.5l6 3.5-6 3.5v-7z" fill={color} stroke="none" /></svg>
    case 'clock': return <svg {...p}><circle cx="12" cy="12" r="9" /><path d="M12 7.5V12l3 2" /></svg>
    case 'calendar': return <svg {...p}><rect x="3.5" y="5" width="17" height="16" rx="2.4" /><path d="M3.5 9.5h17M8 3v4M16 3v4" /></svg>
    case 'message': return <svg {...p}><path strokeLinecap="round" d="M8.5 14.5h7m-7-5H12" /><path d="M14.17 20.89c4.184-.277 7.516-3.657 7.79-7.9c.053-.83.053-1.69 0-2.52c-.274-4.242-3.606-7.62-7.79-7.899a33 33 0 0 0-4.34 0c-4.184.278-7.516 3.657-7.79 7.9a20 20 0 0 0 0 2.52c.1 1.545.783 2.976 1.588 4.184c.467.845.159 1.9-.328 2.823c-.35.665-.526.997-.385 1.237c.14.24.455.248 1.084.263c1.245.03 2.084-.322 2.75-.813c.377-.279.566-.418.696-.434s.387.09.899.3c.46.19.995.307 1.485.34c1.425.094 2.914.094 4.342 0Z" /></svg>
    case 'emoji': return <svg {...p} viewBox="0 0 16 16" fill={color} stroke="none"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16" /><path d="M4.285 9.567a.5.5 0 0 1 .683.183A3.5 3.5 0 0 0 8 11.5a3.5 3.5 0 0 0 3.032-1.75a.5.5 0 1 1 .866.5A4.5 4.5 0 0 1 8 12.5a4.5 4.5 0 0 1-3.898-2.25a.5.5 0 0 1 .183-.683M7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5m4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5" /></svg>
    case 'reply': return <svg {...p} viewBox="0 0 16 16" fill={color} stroke="none"><path d="M13.5 3a.5.5 0 0 1 .5.5A5.5 5.5 0 0 1 8.5 9H3.707l2.647 2.646a.5.5 0 0 1-.708.708l-3.5-3.5a.5.5 0 0 1 0-.708l3.5-3.5a.5.5 0 1 1 .708.708L3.707 8H8.5A4.5 4.5 0 0 0 13 3.5a.5.5 0 0 1 .5-.5" /></svg>
    case 'message-add': return <svg {...p}><path d="M12.5 3.004a33 33 0 0 0-2.67.067c-4.184.278-7.516 3.657-7.79 7.9a20 20 0 0 0 0 2.52c.1 1.545.783 2.976 1.588 4.184c.467.845.159 1.9-.328 2.823c-.35.665-.526.997-.385 1.237c.14.24.455.248 1.084.263c1.245.03 2.084-.322 2.75-.813c.377-.279.566-.418.696-.434s.387.09.899.3c.46.19.995.307 1.485.34c1.425.094 2.914.094 4.342 0c4.183-.278 7.515-3.658 7.789-7.9c.042-.655.051-1.328.027-1.991M8.5 15h7m-7-5H12m3-4.5h7M18.5 2v7" /></svg>
    case 'alert': return <svg {...p}><path d="M12 3.5l9.5 16.5H2.5L12 3.5z" /><path d="M12 9.5v4.5" /><circle cx="12" cy="17.5" r=".6" fill={color} /></svg>
    case 'info': return <svg {...p}><circle cx="12" cy="12" r="9" /><path d="M12 11v5" /><circle cx="12" cy="7.8" r=".6" fill={color} /></svg>
    case 'bug': return <svg {...p}><rect x="8" y="6" width="8" height="13" rx="4" /><path d="M8 10H4M8 14H3.5M8 18l-3.5 2M16 10h4M16 14h4.5M16 18l3.5 2M9 6l-1.5-2.5M15 6l1.5-2.5" /></svg>
    case 'zap': return <svg {...p}><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z" /></svg>
    case 'target': return <svg {...p}><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1.2" fill={color} stroke="none" /></svg>
    case 'trash': return <svg {...p}><path d="M4 7h16M9 7V4.5h6V7M6 7l1 13h10l1-13" /></svg>
    case 'edit': return <svg {...p}><path d="M16.5 4.5l3 3L8 19l-4 1 1-4L16.5 4.5z" /></svg>
    case 'key': return <svg {...p}><circle cx="8" cy="15" r="4.5" /><path d="M11 12l8-8M16 7l2.5 2.5M14 9l2 2" /></svg>
    case 'file': return <svg {...p}><path d="M7 3h7l5 5v13H7V3z" /><path d="M14 3v5h5M9.5 13h6M9.5 16.5h6" /></svg>
    case 'external': return <svg {...p}><path d="M14 5h5v5M19 5l-8 8M18 14v4a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2h4" /></svg>
    case 'user': return <svg {...p}><circle cx="12" cy="8" r="4" /><path d="M4 20c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5" /></svg>
    case 'users': return <svg {...p}><circle cx="9" cy="8" r="3.4" /><path d="M3 20c0-3.4 2.7-5.5 6-5.5s6 2.1 6 5.5" /><path d="M16 5.2a3.4 3.4 0 010 6.3M17.5 14.6c2.4.6 4 2.3 4 5" /></svg>
    case 'refresh': return <svg {...p}><path d="M3 12a9 9 0 0115.5-6.2L21 8M21 4v4h-4M21 12a9 9 0 01-15.5 6.2L3 16M3 20v-4h4" /></svg>
    case 'logout': return <svg {...p}><path d="M15 4h3.5a1.5 1.5 0 011.5 1.5v13a1.5 1.5 0 01-1.5 1.5H15M10 16l-4-4 4-4M6 12h11" /></svg>
    case 'grip': return <svg {...p}><circle cx="9" cy="6" r="1.3" fill={color} stroke="none" /><circle cx="15" cy="6" r="1.3" fill={color} stroke="none" /><circle cx="9" cy="12" r="1.3" fill={color} stroke="none" /><circle cx="15" cy="12" r="1.3" fill={color} stroke="none" /><circle cx="9" cy="18" r="1.3" fill={color} stroke="none" /><circle cx="15" cy="18" r="1.3" fill={color} stroke="none" /></svg>
    case 'quote': return <svg {...p}><path d="M9 7H5.5A1.5 1.5 0 004 8.5V12h5V7zM9 12c0 3-1.6 4.4-3.5 5M20 7h-3.5A1.5 1.5 0 0015 8.5V12h5V7zm0 5c0 3-1.6 4.4-3.5 5" /></svg>
    case 'forward': return <svg {...p}><path d="M14 7l5 5-5 5" /><path d="M19 12H9.5A5.5 5.5 0 004 17.5V19" /></svg>
    case 'send': return <svg {...p}><path d="M21 4L3 11l6.5 2.5L12 20l3-7.5L21 4z" /></svg>
    case 'flag': return <svg {...p}><path d="M5 21V4M5 4h12l-2.5 4L17 12H5" /></svg>
    case 'figma': return <svg {...p}><path d="M8.5 3h3.5v6H8.5a3 3 0 010-6z" /><path d="M12 3h3.5a3 3 0 010 6H12V3z" /><path d="M8.5 9H12v6H8.5a3 3 0 010-6z" /><circle cx="15" cy="12" r="3" /><path d="M8.5 15H12v3a3 3 0 11-3.5-3z" /></svg>
    case 'sparkle': return <svg {...p}><path d="M12 3l1.8 5.4L19 10l-5.2 1.6L12 17l-1.8-5.4L5 10l5.2-1.6L12 3z" /></svg>
    case 'dashboard': return <svg {...p}><rect x="3" y="3" width="8" height="10" rx="1.6" /><rect x="3" y="16" width="8" height="5" rx="1.6" /><rect x="13" y="3" width="8" height="5" rx="1.6" /><rect x="13" y="11" width="8" height="10" rx="1.6" /></svg>
    case 'moon': return <svg {...p}><path d="M20 14.5A8 8 0 119.5 4 6.3 6.3 0 0020 14.5z" /></svg>
    default: return <svg {...p}><circle cx="12" cy="12" r="9" /></svg>
  }
}

export default Icon
