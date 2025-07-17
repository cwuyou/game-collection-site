import { promises as fs } from 'fs'
import path from 'path'
import { GameCard } from '@/components/game-card'

// 分类名称标准化映射
const categoryMapping: { [key: string]: string } = {
  'Girls': 'Girl',
  'Girl': 'Girl',
  'Sports': 'Sports',
  'Sport': 'Sports',
  'Spor': 'Sports'
}

// 标准化分类名称
function normalizeCategory(category: string): string {
  return categoryMapping[category] || category
}

// 分类描述映射
const categoryDescriptions: { [key: string]: string } = {
  "2 Player": "Challenge your friends in our collection of two-player games. Perfect for friendly competition and multiplayer fun.",
  "2D": "Classic 2D games with timeless gameplay and retro charm.",
  "Action": "Fast-paced action games that test your reflexes and skills.",
  "Adventure": "Embark on epic journeys and explore fascinating worlds in our adventure games.",
  "Arcade": "Classic arcade-style games that bring back the golden age of gaming.",
  "Car": "Get behind the wheel in our exciting collection of car games.",
  "Cards": "Classic card games and innovative card-based challenges for all skill levels.",
  "Clicker": "Addictive clicking games that are easy to play but hard to master.",
  "Crazy": "Wild and wacky games that defy expectations.",
  "Drift": "Master the art of drifting in these thrilling racing games.",
  "Driving": "Experience the thrill of driving various vehicles in realistic environments.",
  "Girl": "Games designed with girl gamers in mind, featuring fashion, creativity, and more.",
  "Jump & Run": "Classic platformer games where timing and precision are key to success.",
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
  description?: string
}

async function getGamesForCategory(categoryName: string): Promise<GameData[]> {
  const projectRoot = process.cwd()
  const scrapedDataDir = path.join(projectRoot, 'scraped_data')
  const games: GameData[] = []

  // 处理目录名称的函数
  function getCategoryDirName(category: string): string {
    return category.toLowerCase()
      .replace(/\s*&\s*/g, '_')  // 处理 & 前后可能的空格
      .replace(/\s+/g, '_')      // 处理其他空格
  }

  try {
    // 读取所有子目录
    const subdirs = await fs.readdir(scrapedDataDir)
    
    for (const subdir of subdirs) {
      const subdirPath = path.join(scrapedDataDir, subdir)
      const stats = await fs.stat(subdirPath)
      
      if (stats.isDirectory()) {
        // 如果是 html5games 目录，需要处理其子目录
        if (subdir === 'html5games') {
          const categoryDirName = getCategoryDirName(categoryName)
          const categoryPath = path.join(subdirPath, categoryDirName)
          
          console.log('Looking for category in:', categoryPath) // 调试日志
          
          if (await fs.access(categoryPath).then(() => true).catch(() => false)) {
            const files = await fs.readdir(categoryPath)
            const jsonFiles = files.filter(file => file.endsWith('.json'))
            
            for (const file of jsonFiles) {
              try {
                const filePath = path.join(categoryPath, file)
                const content = await fs.readFile(filePath, 'utf-8')
                const gameData = JSON.parse(content)
                
                // 检查游戏的分类是否匹配（考虑标准化后的分类名称）
                const normalizedGameCategories = (gameData.categories || []).map(normalizeCategory)
                const normalizedCategoryName = normalizeCategory(categoryName)
                
                if (normalizedGameCategories.includes(normalizedCategoryName)) {
                  const game: GameData = {
                    id: file.replace('.json', ''),
                    source: 'html5games',
                    title: gameData.title || 'Untitled Game',
                    preview_image: gameData.preview_image || '/placeholder.jpg',
                    categories: normalizedGameCategories,
                    description: gameData.description
                  }
                  games.push(game)
                }
              } catch (error) {
                console.error(`Error processing file ${file}:`, error)
              }
            }
          }
        } else {
          // 对于其他目录，读取所有 JSON 文件并检查分类
          const files = await fs.readdir(subdirPath)
          const jsonFiles = files.filter(file => file.endsWith('.json'))
          
          for (const file of jsonFiles) {
            try {
              const filePath = path.join(subdirPath, file)
              const content = await fs.readFile(filePath, 'utf-8')
              const gameData = JSON.parse(content)
              
              // 标准化游戏的分类名称
              const normalizedCategories = (gameData.categories || []).map(normalizeCategory)
              
              // 检查游戏是否属于当前分类（考虑标准化后的分类名称）
              const normalizedCategoryName = normalizeCategory(categoryName)
              if (normalizedCategories.includes(normalizedCategoryName)) {
                const game: GameData = {
                  id: file.replace('.json', ''),
                  source: subdir,
                  title: gameData.title || 'Untitled Game',
                  preview_image: gameData.preview_image || '/placeholder.jpg',
                  categories: normalizedCategories,
                  description: gameData.description
                }
                games.push(game)
              }
            } catch (error) {
              console.error(`Error processing file ${file} in directory ${subdir}:`, error)
            }
          }
        }
      } else if (stats.isFile() && subdir.endsWith('.json')) {
        // 处理根目录下的 JSON 文件
        try {
          const filePath = path.join(scrapedDataDir, subdir)
          const content = await fs.readFile(filePath, 'utf-8')
          const gameData = JSON.parse(content)
          
          // 标准化游戏的分类名称
          const normalizedCategories = (gameData.categories || []).map(normalizeCategory)
          
          // 检查游戏是否属于当前分类（考虑标准化后的分类名称）
          const normalizedCategoryName = normalizeCategory(categoryName)
          if (normalizedCategories.includes(normalizedCategoryName)) {
            const game: GameData = {
              id: subdir.replace('.json', ''),
              source: 'root',
              title: gameData.title || 'Untitled Game',
              preview_image: gameData.preview_image || '/placeholder.jpg',
              categories: normalizedCategories,
              description: gameData.description
            }
            games.push(game)
          }
        } catch (error) {
          console.error(`Error processing root file ${subdir}:`, error)
        }
      }
    }
  } catch (error) {
    console.error(`Error reading games for category ${categoryName}:`, error)
  }

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