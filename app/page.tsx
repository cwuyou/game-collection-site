"use client"

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { GameContent } from '@/components/game-content'
import { Header } from '@/components/header'
import { useGameStore } from '@/lib/store'

export default function Home() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const { setGames } = useGameStore()

  useEffect(() => {
    async function loadGames() {
      try {
        const response = await fetch('/api/games')
        const games = await response.json()
        setGames(games)
      } catch (error) {
        console.error('Failed to load games:', error)
      }
    }

    loadGames()
  }, [setGames])

  return (
    <div className="min-h-screen bg-gray-900">
      <Header onMenuToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
        <main className="flex-1 overflow-y-auto">
          <GameContent />
        </main>
      </div>
    </div>
  )
}
