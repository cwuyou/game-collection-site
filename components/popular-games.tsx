import { ChevronRight } from "lucide-react"
import { GameCard } from "@/components/game-card"

const popularGames = [
  {
    id: 1,
    title: "Halloween merge",
    rating: 75,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-purple-600 to-purple-800",
  },
  {
    id: 2,
    title: "Stand on the right color, Robby!",
    rating: 69,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-cyan-400 to-blue-500",
  },
  {
    id: 3,
    title: "Dark Lands: Online RPG",
    rating: 68,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-gray-700 to-gray-900",
  },
  {
    id: 4,
    title: "Crazy Crash Landing",
    rating: 70,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-green-400 to-cyan-500",
  },
  {
    id: 5,
    title: "Net Fighters",
    rating: 75,
    image: "/placeholder.svg?height=200&width=300",
    gradient: "from-green-500 to-green-700",
  },
]

export function PopularGames() {
  return (
    <section className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg lg:text-xl font-semibold text-white">Popular</h2>
        <button className="text-green-400 hover:text-green-300 text-sm font-medium flex items-center">
          All
          <ChevronRight className="w-4 h-4 ml-1" />
        </button>
      </div>

      <div className="flex space-x-3 lg:space-x-4 overflow-x-auto pb-4 scrollbar-hide">
        {popularGames.map((game) => (
          <GameCard key={game.id} game={game} />
        ))}
      </div>
    </section>
  )
}
