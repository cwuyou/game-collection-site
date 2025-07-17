import { NextResponse } from 'next/server'
import fs from 'fs/promises'
import path from 'path'

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

// 处理目录名称的函数
function getCategoryDirName(category: string): string {
  return category.toLowerCase()
  .replace(/\s*&\s*/g, '_')  // 处理 & 前后可能的空格
  .replace(/\s+/g, '_')      // 处理其他空格
}

export async function GET() {
  try {
    const dataDir = path.join(process.cwd(), 'scraped_data')
    const games: any[] = []

    // 读取所有子目录
    const subdirs = await fs.readdir(dataDir)
    
    for (const subdir of subdirs) {
      const subdirPath = path.join(dataDir, subdir)
      const stats = await fs.stat(subdirPath)
      
      if (stats.isDirectory()) {
        // 如果是 html5games 目录，需要处理其子目录
        if (subdir === 'html5games') {
          const categoryDirs = await fs.readdir(subdirPath)
          for (const categoryDir of categoryDirs) {
            const categoryPath = path.join(subdirPath, categoryDir)
            const categoryStats = await fs.stat(categoryPath)
            
            if (categoryStats.isDirectory()) {
              const files = await fs.readdir(categoryPath)
              const jsonFiles = files.filter(file => file.endsWith('.json'))
              
              for (const file of jsonFiles) {
                try {
                  const filePath = path.join(categoryPath, file)
                  const content = await fs.readFile(filePath, 'utf-8')
                  const gameData = JSON.parse(content)
                  
                  // 从目录名还原分类名
                  const categoryName = categoryDir
                    .replace(/_/g, ' ')
                    .replace(/\b\w/g, l => l.toUpperCase())
                  
                  // 标准化分类名称
                  const normalizedCategory = normalizeCategory(categoryName)
                  
                  gameData.source = 'html5games'
                  gameData.id = file.replace('.json', '')
                  gameData.categories = [normalizedCategory]
                  games.push(gameData)
                } catch (error) {
                  console.error(`Error processing file ${file} in category ${categoryDir}:`, error)
                }
              }
            }
          }
        } else {
          // 对于其他目录，直接读取 JSON 文件
          const files = await fs.readdir(subdirPath)
          const jsonFiles = files.filter(file => file.endsWith('.json'))
          
          for (const file of jsonFiles) {
            try {
              const filePath = path.join(subdirPath, file)
              const content = await fs.readFile(filePath, 'utf-8')
              const gameData = JSON.parse(content)
              
              // 标准化所有分类名称
              const normalizedCategories = (gameData.categories || []).map((cat: string) => normalizeCategory(cat))
              
              gameData.source = subdir
              gameData.id = file.replace('.json', '')
              gameData.categories = normalizedCategories
              games.push(gameData)
            } catch (error) {
              console.error(`Error processing file ${file} in directory ${subdir}:`, error)
            }
          }
        }
      } else if (stats.isFile() && subdir.endsWith('.json')) {
        // 处理根目录下的 JSON 文件
        try {
          const filePath = path.join(dataDir, subdir)
          const content = await fs.readFile(filePath, 'utf-8')
          const gameData = JSON.parse(content)
          
          // 标准化所有分类名称
          const normalizedCategories = (gameData.categories || []).map((cat: string) => normalizeCategory(cat))
          
          gameData.source = 'root'
          gameData.id = subdir.replace('.json', '')
          gameData.categories = normalizedCategories
          games.push(gameData)
        } catch (error) {
          console.error(`Error processing root file ${subdir}:`, error)
        }
      }
    }

    return NextResponse.json(games)
  } catch (error) {
    console.error('Error reading games:', error)
    return NextResponse.json({ error: 'Failed to load games' }, { status: 500 })
  }
} 