import { useGameStore } from '@/lib/store'
import { GameDetail } from './game-detail'
import Image from 'next/image'
import { useEffect, useRef } from 'react'

const categoryDescriptions: Record<string, string> = {
  'All games': 'Browse our complete collection of free online games.',
  'New': 'Check out our latest additions to the game library.',
  'Popular': 'Most played and loved games by our community.',
  '2 Player': 'Games you can enjoy with a friend on the same device.',
  '2D': 'Classic two-dimensional games with timeless appeal.',
  'Action': 'Fast-paced games full of excitement and adventure.',
  'Adventure': 'Explore new worlds and embark on epic quests.',
  'Arcade': 'Classic arcade-style games that never go out of style.',
  'Car': 'Racing, driving, and car-themed games for speed enthusiasts.',
  'Clicker': 'Addictive clicking games that test your speed.',
  'Crazy': 'Wild and wacky games that defy expectations.',
  'Drift': 'Master the art of drifting in these racing games.',
  'Driving': 'Get behind the wheel in these realistic driving simulations.',
  'Girl': 'Games designed with female players in mind.',
  'Kids': 'Fun and educational games suitable for children.',
  'Mobile': 'Games optimized for mobile devices.',
  'Multiplayer': 'Play with friends or compete against players worldwide.',
  'Pixel': 'Retro-style games with classic pixel art graphics.',
  'Puzzle': 'Challenge your mind with brain-teasing puzzles.',
  'Racing': 'Compete in high-speed races across various tracks.',
  'Shooting': 'Test your aim in these action-packed shooting games.',
  'Simulator': 'Experience realistic simulations of various activities.',
  'Sniper': 'Precision shooting games that test your accuracy.',
  'Sports': 'Athletic competitions and sports-themed games.',
  'Strategy': 'Plan your moves and outsmart your opponents.',
}

export function GameContent() {
  const { selectedCategory, selectedGame, games, setSelectedGame } = useGameStore()
  const previousCategory = useRef(selectedCategory)
  
  // 只在分类变化时，且在游戏详情页面时，才返回到分类页面
  useEffect(() => {
    if (selectedCategory !== previousCategory.current && selectedGame) {
      setSelectedGame(null)
    }
    previousCategory.current = selectedCategory
  }, [selectedCategory, selectedGame, setSelectedGame])

  if (selectedGame) {
    return <GameDetail game={selectedGame} onBack={() => setSelectedGame(null)} />
  }

  const filteredGames = selectedCategory === 'All games' 
    ? games 
    : games.filter(game => game.categories.includes(selectedCategory))

  return (
    <div className="flex-1 p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-3">{selectedCategory}</h1>
        <p className="text-gray-300">
          {categoryDescriptions[selectedCategory] || `Explore our collection of ${selectedCategory} games.`}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {filteredGames.map((game, index) => (
          <div 
            key={index} 
            className="bg-gray-800 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors cursor-pointer"
            onClick={() => setSelectedGame(game)}
          >
            <div className="relative aspect-square">
              <Image
                src={game.preview_image}
                alt={game.title}
                fill
                className="object-cover"
              />
            </div>
            <div className="p-2 text-center">
              <h3 className="text-white font-medium text-sm truncate">{game.title}</h3>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 