"use client"

import { Search, User, Settings, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface HeaderProps {
  onMenuToggle: () => void
}

export function Header({ onMenuToggle }: HeaderProps) {
  return (
    <header className="bg-gray-800 border-b border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center space-x-4">
          {/* Mobile menu button - 只在lg屏幕以下显示 */}
          <button
            onClick={onMenuToggle}
            className="lg:hidden text-gray-300 hover:text-white p-1 rounded-md hover:bg-gray-700 transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>

          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">P</span>
            </div>
            <span className="text-xl font-bold text-white">playhop</span>
          </div>
        </div>

        <div className="flex-1 max-w-md mx-4 lg:mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              type="text"
              placeholder="Find game or genre"
              className="w-full pl-10 bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-green-500"
            />
          </div>
        </div>

        <div className="flex items-center space-x-2 lg:space-x-4">
          <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white hidden sm:flex">
            <Settings className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white hidden sm:flex">
            <User className="w-4 h-4" />
          </Button>
          <Button className="bg-green-500 hover:bg-green-600 text-white px-3 lg:px-4 py-2 rounded-lg text-sm">
            Log in
          </Button>
        </div>
      </div>
    </header>
  )
}
