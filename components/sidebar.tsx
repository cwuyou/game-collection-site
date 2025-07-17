"use client"

import { useGameStore } from '@/lib/store'
import {
  Home,
  Star,
  Zap,
  Gamepad2,
  Swords,
  Map,
  Globe,
  LayoutGrid,
  CircleUser,
  Dices,
  Pencil,
  Shirt,
  Sword,
  Crosshair,
  Search,
  Skull,
  Brain,
  Grid2x2 as GridIcon,
  Puzzle,
  Users,
  Car,
  Target,
  Monitor,
  Trophy,
  Castle,
  Text,
  Box,
  X,
} from "lucide-react"

const categories = [
  { icon: Home, label: "All games", href: "/" },
  { icon: Zap, label: "New", href: "/new", count: 307, highlight: true },
  { icon: Star, label: "Popular", href: "/popular" },
  { icon: Gamepad2, label: "All categories", href: "/categories", separator: true },
  { icon: Users, label: "2 Player", href: "/category/2%20Player" },
  { icon: Box, label: "2D", href: "/category/2D" },
  { icon: Swords, label: "Action", href: "/category/Action" },
  { icon: Map, label: "Adventure", href: "/category/Adventure" },
  { icon: Gamepad2, label: "Arcade", href: "/category/Arcade" },
  { icon: Car, label: "Car", href: "/category/Car" },
  { icon: Dices, label: "Cards", href: "/category/Cards" },  // 添加 Cards 分类
  { icon: Gamepad2, label: "Clicker", href: "/category/Clicker" },
  { icon: Gamepad2, label: "Crazy", href: "/category/Crazy" },
  { icon: Car, label: "Drift", href: "/category/Drift" },
  { icon: Car, label: "Driving", href: "/category/Driving" },
  { icon: Shirt, label: "Girl", href: "/category/Girl" },
  { icon: Gamepad2, label: "Jump & Run", href: "/category/Jump%20%26%20Run" },  // 添加 Jump & Run 分类
  { icon: Dices, label: "Kids", href: "/category/Kids" },
  { icon: Monitor, label: "Mobile", href: "/category/Mobile" },
  { icon: Users, label: "Multiplayer", href: "/category/Multiplayer" },
  { icon: GridIcon, label: "Pixel", href: "/category/Pixel" },
  { icon: Puzzle, label: "Puzzle", href: "/category/Puzzle" },
  { icon: Car, label: "Racing", href: "/category/Racing" },
  { icon: Target, label: "Shooting", href: "/category/Shooting" },
  { icon: Monitor, label: "Simulator", href: "/category/Simulator" },
  { icon: Crosshair, label: "Sniper", href: "/category/Sniper" },
  { icon: Trophy, label: "Sports", href: "/category/Sports" },
  { icon: Brain, label: "Strategy", href: "/category/Strategy" },
  { icon: Gamepad2, label: "All tags", href: "/tags", separator: true },
]

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { setSelectedCategory } = useGameStore()

  const handleCategoryClick = (e: React.MouseEvent<HTMLAnchorElement>, category: string) => {
    e.preventDefault()
    setSelectedCategory(category)
    if (window.innerWidth < 1024) {
      onToggle()
    }
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden" 
          onClick={onToggle}
          aria-hidden="true"
        />
      )}

      {/* Mobile Sidebar */}
      <div
        className={`
          fixed inset-y-0 left-0 z-50 lg:hidden
          w-64 bg-gray-800 border-r border-gray-700 
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        <div className="flex justify-between items-center p-4 border-b border-gray-700">
          <span className="text-lg font-semibold text-white">Categories</span>
          <button 
            onClick={onToggle} 
            className="text-gray-400 hover:text-white"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="h-[calc(100vh-4rem)] overflow-y-auto">
          <div className="p-3">
            <nav className="space-y-1">
              {categories.map((category, index) => {
                const Icon = category.icon
                return (
                  <div key={index}>
                    {category.separator && <div className="border-t border-gray-700 my-2" />}
                    <a
                      href={category.href}
                      onClick={(e) => handleCategoryClick(e, category.label)}
                      className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-base transition-colors ${
                        category.highlight
                          ? "bg-green-500/10 text-green-400 hover:bg-green-500/20"
                          : "text-gray-300 hover:bg-gray-700 hover:text-white"
                      }`}
                    >
                      <div className="flex items-center space-x-3 min-w-0">
                        <Icon className="w-4 h-4 flex-shrink-0" />
                        <span className="font-medium text-base">{category.label}</span>
                      </div>
                      {category.count && (
                        <span
                          className={`text-sm px-2 py-1 rounded-full flex-shrink-0 ml-2 ${
                            category.highlight ? "bg-green-500 text-white" : "bg-gray-600 text-gray-300"
                          }`}
                        >
                          {category.count}
                        </span>
                      )}
                    </a>
                  </div>
                )
              })}
            </nav>
            <div className="mt-4 text-xs text-gray-500">hidden treasures 2326</div>
          </div>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden lg:block w-48 xl:w-52 flex-shrink-0">
        <div className="h-full bg-gray-800 border-r border-gray-700">
          <div className="h-full overflow-y-auto">
            <div className="p-2">
              <nav className="space-y-0.5">
                {categories.map((category, index) => {
                  const Icon = category.icon
                  return (
                    <div key={index}>
                      {category.separator && <div className="border-t border-gray-700 my-1.5" />}
                      <a
                        href={category.href}
                        onClick={(e) => handleCategoryClick(e, category.label)}
                        className={`flex items-center justify-between px-3 py-2 rounded-lg text-base transition-colors ${
                          category.highlight
                            ? "bg-green-500/10 text-green-400 hover:bg-green-500/20"
                            : "text-gray-300 hover:bg-gray-700 hover:text-white"
                        }`}
                      >
                        <div className="flex items-center space-x-3 min-w-0">
                          <Icon className="w-4 h-4 flex-shrink-0" />
                          <span className="font-medium text-base">{category.label}</span>
                        </div>
                        {category.count && (
                          <span
                            className={`text-xs px-1 py-0.5 rounded-full flex-shrink-0 ml-1.5 ${
                              category.highlight ? "bg-green-500 text-white" : "bg-gray-600 text-gray-300"
                            }`}
                          >
                            {category.count}
                          </span>
                        )}
                      </a>
                    </div>
                  )
                })}
              </nav>
              <div className="mt-4 text-xs text-gray-500">hidden treasures 2326</div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
