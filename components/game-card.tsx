import Image from "next/image"

interface Game {
  id: number
  title: string
  rating: number
  image: string
  gradient: string
}

interface GameCardProps {
  game: Game
}

export function GameCard({ game }: GameCardProps) {
  return (
    <div className="flex-shrink-0 w-48 sm:w-56 lg:w-64 group cursor-pointer">
      <div className="relative rounded-lg overflow-hidden mb-3">
        <div className={`absolute inset-0 bg-gradient-to-br ${game.gradient}`} />
        <div className="relative aspect-video">
          <Image
            src={game.image || "/placeholder.svg"}
            alt={game.title}
            fill
            className="object-cover opacity-80 group-hover:opacity-100 transition-opacity"
          />
        </div>
        <div className="absolute top-2 left-2">
          <span className="bg-black/50 text-white text-xs px-2 py-1 rounded-full">{game.rating}</span>
        </div>
      </div>
      <h3 className="text-white text-sm font-medium group-hover:text-green-400 transition-colors line-clamp-2">
        {game.title}
      </h3>
    </div>
  )
}
