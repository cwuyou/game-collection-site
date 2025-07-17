import { promises as fs } from 'fs'
import path from 'path'
import { GameDetail } from '@/components/game-detail'

interface GameDetailPageProps {
  params: {
    source: string
    id: string
  }
}

export default async function GameDetailPage({ params }: GameDetailPageProps) {
  const { source, id } = params
  const projectRoot = process.cwd()
  const scrapedDataDir = path.join(projectRoot, 'scraped_data')

  let filePath: string
  if (source === 'root') {
    filePath = path.join(scrapedDataDir, `${id}.json`)
  } else {
    filePath = path.join(scrapedDataDir, source, `${id}.json`)
  }

  try {
    const content = await fs.readFile(filePath, 'utf-8')
    const game = JSON.parse(content)
    game.source = source
    game.id = id

    return (
      <GameDetail 
        game={game} 
        onBack={() => {}} // 这个函数在客户端组件中会被覆盖
      />
    )
  } catch (error) {
    console.error(`Error loading game ${id} from ${source}:`, error)
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold text-white mb-4">Game Not Found</h1>
        <p className="text-gray-400">Sorry, we couldn't find the game you're looking for.</p>
      </div>
    )
  }
} 