"use client"
import {
  Home,
  Star,
  Zap,
  Gamepad2,
  Sword,
  Mountain,
  Joystick,
  BookOpen,
  Target,
  Users,
  Heart,
  Ghost,
  Trophy,
  Puzzle,
  HelpCircle,
  Crown,
  Car,
  User,
  Dumbbell,
  Brain,
  Shuffle,
  Hash,
  X,
} from "lucide-react"

const categories = [
  { icon: Home, label: "All games", count: null },
  { icon: Zap, label: "New", count: 307, highlight: true },
  { icon: Star, label: "Popular", count: null },
  { icon: Hash, label: "All categories", count: null, separator: true },
  { icon: Gamepad2, label: ".io Games", count: null },
  { icon: Sword, label: "Action", count: null },
  { icon: Mountain, label: "Adventure", count: null },
  { icon: Joystick, label: "Arcade", count: null },
  { icon: BookOpen, label: "Board", count: null },
  { icon: Target, label: "Bubble shooters", count: null },
  { icon: Heart, label: "Card", count: null },
  { icon: Users, label: "Casual", count: null },
  { icon: Crown, label: "Economy", count: null },
  { icon: Brain, label: "Educational", count: null },
  { icon: User, label: "For boys", count: null },
  { icon: Heart, label: "For girls", count: null },
  { icon: Ghost, label: "Horror", count: null },
  { icon: Trophy, label: "Match 3", count: null },
  { icon: Target, label: "Midcore", count: null },
  { icon: BookOpen, label: "Novels", count: null },
  { icon: Puzzle, label: "Puzzles", count: null },
  { icon: HelpCircle, label: "Quiz", count: null },
  { icon: Crown, label: "RPG", count: null },
  { icon: Car, label: "Racing", count: null },
  { icon: Gamepad2, label: "Simulators", count: null },
  { icon: Dumbbell, label: "Sports", count: null },
  { icon: Brain, label: "Strategy", count: null },
  { icon: Shuffle, label: "Two players", count: null },
  { icon: Hash, label: "All tags", count: null, separator: true },
]

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
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
          w-52 bg-gray-800 border-r border-gray-700 
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        <div className="flex justify-between items-center p-2.5 border-b border-gray-700">
          <span className="text-base font-semibold text-white">Categories</span>
          <button 
            onClick={onToggle} 
            className="text-gray-400 hover:text-white"
            aria-label="Close menu"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="h-[calc(100vh-4rem)] overflow-y-auto">
          <div className="p-2">
            <nav className="space-y-0.5">
              {categories.map((category, index) => {
                const Icon = category.icon
                return (
                  <div key={index}>
                    {category.separator && <div className="border-t border-gray-700 my-1.5" />}
                    <a
                      href="#"
                      className={`flex items-center justify-between px-2 py-1.5 rounded-lg text-sm transition-colors ${
                        category.highlight
                          ? "bg-green-500/10 text-green-400 hover:bg-green-500/20"
                          : "text-gray-300 hover:bg-gray-700 hover:text-white"
                      }`}
                    >
                      <div className="flex items-center space-x-2 min-w-0">
                        <Icon className="w-3.5 h-3.5 flex-shrink-0" />
                        <span className="font-medium text-sm">{category.label}</span>
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

      {/* Desktop Sidebar */}
      <div className="hidden lg:block w-48 xl:w-52 flex-shrink-0">
        <div className="h-full bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <div className="p-2">
            <nav className="space-y-0.5">
              {categories.map((category, index) => {
                const Icon = category.icon
                return (
                  <div key={index}>
                    {category.separator && <div className="border-t border-gray-700 my-1.5" />}
                    <a
                      href="#"
                      className={`flex items-center justify-between px-2 py-1.5 rounded-lg text-sm transition-colors ${
                        category.highlight
                          ? "bg-green-500/10 text-green-400 hover:bg-green-500/20"
                          : "text-gray-300 hover:bg-gray-700 hover:text-white"
                      }`}
                    >
                      <div className="flex items-center space-x-2 min-w-0">
                        <Icon className="w-3.5 h-3.5 flex-shrink-0" />
                        <span className="font-medium text-sm">{category.label}</span>
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
    </>
  )
}
