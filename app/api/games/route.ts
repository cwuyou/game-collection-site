import { NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'

export async function GET() {
  try {
    const dataDir = path.join(process.cwd(), 'scraped_data')
    const files = await fs.readdir(dataDir)
    const jsonFiles = files.filter(file => file.endsWith('.json'))
    
    const games = await Promise.all(
      jsonFiles.map(async (file) => {
        const filePath = path.join(dataDir, file)
        const content = await fs.readFile(filePath, 'utf-8')
        return JSON.parse(content)
      })
    )

    return NextResponse.json(games)
  } catch (error) {
    console.error('Failed to load games:', error)
    return NextResponse.json({ error: 'Failed to load games' }, { status: 500 })
  }
} 