import Image from 'next/image'
import Link from 'next/link'

interface GameCardProps {
  title: string
  image?: string
  href: string
}

export function GameCard({ title, image, href }: GameCardProps) {
  // 确保href不为undefined
  if (!href) {
    console.error('GameCard received undefined href for game:', title)
    return null // 如果没有href，不渲染卡片
  }

  return (
    <Link href={href} className="group">
      <div className="relative aspect-[4/3] overflow-hidden rounded-lg bg-gray-900">
        <Image
          src={image || '/placeholder.jpg'}
          alt={title}
          fill
          className="object-cover transition-transform group-hover:scale-105"
        />
      </div>
      <h3 className="mt-2 text-lg font-semibold">{title}</h3>
    </Link>
  )
}
