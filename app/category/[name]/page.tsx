import { promises as fs } from 'fs'
import path from 'path'
import { GameCard } from '@/components/game-card'

// 分类描述映射
const categoryDescriptions: { [key: string]: string } = {
  "2 Player": "Challenge your friends in our collection of two-player games. Perfect for friendly competition and multiplayer fun.",
  "2D": "Classic 2D games with timeless gameplay and retro charm.",
  "Action": "Fast-paced action games that test your reflexes and skills.",
  "Adventure": "Embark on epic journeys and explore fascinating worlds in our adventure games.",
  "Arcade": "Classic arcade-style games that bring back the golden age of gaming.",
  "Car": "Get behind the wheel in our exciting collection of car games.",
  "Clicker": "Addictive clicking games that are easy to play but hard to master.",
  "Crazy": "Wild and wacky games that defy expectations.",
  "Drift": "Master the art of drifting in these thrilling racing games.",
  "Driving": "Experience the thrill of driving various vehicles in realistic environments.",
  "Girl": "Games designed with girl gamers in mind, featuring fashion, creativity, and more.",
  "Kids": "Fun and educational games perfect for young players.",
  "Mobile": "Games optimized for mobile play, perfect for gaming on the go.",
  "Multiplayer": "Connect and compete with players from around the world.",
  "Pixel": "Retro-styled pixel art games with classic charm.",
  "Puzzle": "Challenge your mind with our collection of brain-teasing puzzle games.",
  "Racing": "Speed through tracks and compete for first place in our racing games.",
  "Shooting": "Test your aim and reflexes in our action-packed shooting games.",
  "Simulator": "Experience realistic simulations of various activities and professions.",
  "Sniper": "Precision shooting games that test your accuracy and patience.",
  "Sports": "Compete in various sports games from football to basketball and more.",
  "Strategy": "Plan your moves and outsmart opponents in our strategy games."
}

interface GameData {
  id: string
  source: string
  title: string
  preview_image: string
  categories: string[]
}

async function getGamesForCategory(categoryName: string): Promise<GameData[]> {
  const projectRoot = process.cwd()
  const scrapedDataDir = path.join(projectRoot, 'scraped_data')
  const games: GameData[] = []

  // 读取1000webgames目录
  try {
    const webgamesDir = path.join(scrapedDataDir, '1000webgames')
    if (await fs.access(webgamesDir).then(() => true).catch(() => false)) {
      const files = await fs.readdir(webgamesDir)
      for (const file of files) {
        if (file.endsWith('.json')) {
          try {
            const content = await fs.readFile(path.join(webgamesDir, file), 'utf-8')
            const gameData = JSON.parse(content)
            if (gameData.categories?.includes(categoryName)) {
              const game: GameData = {
                id: file.replace('.json', ''),
                source: '1000webgames',
                title: gameData.title || 'Untitled Game',
                preview_image: gameData.preview_image || '/placeholder.jpg',
                categories: gameData.categories || []
              }
              games.push(game)
            }
          } catch (error) {
            console.error(`Error processing file ${file} in 1000webgames:`, error)
          }
        }
      }
    }
  } catch (error) {
    console.error('Error reading 1000webgames directory:', error)
  }

  // 读取jopi目录
  try {
    const jopiDir = path.join(scrapedDataDir, 'jopi')
    if (await fs.access(jopiDir).then(() => true).catch(() => false)) {
      const files = await fs.readdir(jopiDir)
      for (const file of files) {
        if (file.endsWith('.json')) {
          try {
            const content = await fs.readFile(path.join(jopiDir, file), 'utf-8')
            const gameData = JSON.parse(content)
            if (gameData.categories?.includes(categoryName)) {
              const game: GameData = {
                id: file.replace('.json', ''),
                source: 'jopi',
                title: gameData.title || 'Untitled Game',
                preview_image: gameData.preview_image || '/placeholder.jpg',
                categories: gameData.categories || []
              }
              games.push(game)
            }
          } catch (error) {
            console.error(`Error processing file ${file} in jopi:`, error)
          }
        }
      }
    }
  } catch (error) {
    console.error('Error reading jopi directory:', error)
  }

  // 读取根目录下的json文件
  try {
    const files = await fs.readdir(scrapedDataDir)
    for (const file of files) {
      if (file.endsWith('.json')) {
        try {
          const content = await fs.readFile(path.join(scrapedDataDir, file), 'utf-8')
          const gameData = JSON.parse(content)
          if (gameData.categories?.includes(categoryName)) {
            const game: GameData = {
              id: file.replace('.json', ''),
              source: 'root',
              title: gameData.title || 'Untitled Game',
              preview_image: gameData.preview_image || '/placeholder.jpg',
              categories: gameData.categories || []
            }
            games.push(game)
          }
        } catch (error) {
          console.error(`Error processing file ${file} in root:`, error)
        }
      }
    }
  } catch (error) {
    console.error('Error reading root directory:', error)
  }

  // 打印找到的游戏数据以便调试
  console.log(`Found ${games.length} games for category "${categoryName}":`, 
    games.map(g => ({ id: g.id, source: g.source, title: g.title }))
  )

  return games
}

export default async function CategoryPage({ params }: { params: { name: string } }) {
  const categoryName = decodeURIComponent(params.name)
  const games = await getGamesForCategory(categoryName)
  const description = categoryDescriptions[categoryName] || `Browse our collection of ${categoryName.toLowerCase()} games.`

  // 验证每个游戏对象的完整性
  const validGames = games.filter(game => {
    const isValid = game && game.id && game.source && game.title
    if (!isValid) {
      console.error('Invalid game data:', game)
    }
    return isValid
  })

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-2">{categoryName}</h1>
      <p className="text-gray-400 mb-6">{description}</p>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {validGames.map((game) => (
          <GameCard
            key={`${game.source}-${game.id}`}
            title={game.title}
            image={game.preview_image}
            href={`/game/${encodeURIComponent(game.source)}/${encodeURIComponent(game.id)}`}
          />
        ))}
      </div>

      {validGames.length === 0 && (
        <div className="text-center text-gray-400 mt-8">
          No games found in this category.
        </div>
      )}
    </div>
  )
} 