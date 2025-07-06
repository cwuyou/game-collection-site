"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { GameGrid } from "@/components/game-grid"
import { PopularGames } from "@/components/popular-games"

export default function HomePage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header onMenuToggle={toggleSidebar} />
      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar isOpen={sidebarOpen} onToggle={toggleSidebar} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-2xl lg:text-3xl font-bold mb-2">Free Online Games</h1>

            <div className="mb-8">
              <div className="text-gray-400 mb-4">Error 404</div>
              <h2 className="text-lg lg:text-xl mb-2">We couldn't find that page or game,</h2>
              <p className="text-gray-300 mb-6">but here are some of our favorites. Maybe you'll like them too 😍</p>
            </div>

            <PopularGames />
            <GameGrid />
          </div>
        </main>
      </div>
    </div>
  )
}
