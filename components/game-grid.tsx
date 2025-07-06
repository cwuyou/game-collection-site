import { GameCard } from "@/components/game-card"

const allGames = [
  {
    id: 6,
    title: "Bubble Shooter Pro",
    rating: 82,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-blue-500 to-purple-600",
  },
  {
    id: 7,
    title: "Racing Thunder",
    rating: 76,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-red-500 to-orange-600",
  },
  {
    id: 8,
    title: "Magic Quest",
    rating: 79,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-purple-500 to-pink-600",
  },
  {
    id: 9,
    title: "Space Adventure",
    rating: 73,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-indigo-600 to-blue-800",
  },
  {
    id: 10,
    title: "Puzzle Master",
    rating: 85,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-yellow-500 to-orange-500",
  },
  {
    id: 11,
    title: "Tower Defense",
    rating: 71,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-green-600 to-teal-700",
  },
  {
    id: 12,
    title: "Card Battle",
    rating: 68,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-red-600 to-pink-700",
  },
  {
    id: 13,
    title: "Ninja Run",
    rating: 77,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-gray-800 to-black",
  },
]

export function GameGrid() {
  return (
    <section>
      <h2 className="text-lg lg:text-xl font-semibold text-white mb-4">All Games</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-3 lg:gap-4">
        {allGames.map((game) => (
          <div key={game.id} className="w-full">
            <GameCard game={game} />
          </div>
        ))}
      </div>
    </section>
  )
}
