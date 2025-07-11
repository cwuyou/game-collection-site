import { create } from 'zustand'

interface Game {
  title: string
  description: string
  preview_image: string
  categories: string[]
  url: string
  iframe_url: string
  html_content: string
}

interface GameStore {
  selectedCategory: string
  selectedGame: Game | null
  games: Game[]
  setSelectedCategory: (category: string) => void
  setSelectedGame: (game: Game | null) => void
  setGames: (games: Game[]) => void
}

export const useGameStore = create<GameStore>((set) => ({
  selectedCategory: 'All games',
  selectedGame: null,
  games: [],
  setSelectedCategory: (category) => set({ selectedCategory: category }),
  setSelectedGame: (game) => set({ selectedGame: game }),
  setGames: (games) => set({ games }),
})) 