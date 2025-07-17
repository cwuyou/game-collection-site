import { useState } from 'react'
import { ArrowLeft, Maximize } from 'lucide-react'
import { Button } from './ui/button'

interface GameDetailProps {
  game: {
    title: string
    description: string
    iframe_url: string
    html_content: string
  }
  onBack: () => void
}

interface Section {
  title: string
  content: string
  level: number // 1 for main sections, 2 for subsections
}

interface ParsedContent {
  sections: Section[]
}

export function GameDetail({ game, onBack }: GameDetailProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)

  const parseGameContent = (htmlContent: string): ParsedContent => {
    // 如果没有html_content，则使用description创建一个基本的section
    if (!htmlContent) {
      return {
        sections: [{
          title: 'About This Game',
          content: `<p>${game.description || 'No description available.'}</p>`,
          level: 1
        }]
      }
    }

    const parser = new DOMParser()
    const doc = parser.parseFromString(htmlContent, 'text/html')
    
    const content = doc.body.innerHTML
    const postEntryIndex = content.indexOf('<div class="post__entry">')
    const featuredImageIndex = content.indexOf('<figure class="post__featured-image is-loaded">')
    
    if (postEntryIndex !== -1 && featuredImageIndex !== -1) {
      const descriptionHtml = content.substring(postEntryIndex, featuredImageIndex)
      const descriptionDoc = parser.parseFromString(descriptionHtml, 'text/html')
      const sections: Section[] = []
      
      // 获取post__entry div
      const postEntry = descriptionDoc.querySelector('.post__entry')
      if (postEntry) {
        let currentSection: Section = {
          title: 'About This Game',
          content: '',
          level: 1
        }
        
        // 处理所有子节点
        Array.from(postEntry.childNodes).forEach((node) => {
          if (node instanceof Element) {
            // 检查是否是标题元素
            if (node.matches('h1, h2, h3, h4, h5, h6')) {
              // 如果当前部分有内容，保存它
              if (currentSection.content.trim()) {
                sections.push({ ...currentSection })
              }
              
              // 开始新的部分
              currentSection = {
                title: node.textContent?.trim() || 'Game Information',
                content: '',
                level: node.tagName === 'H2' ? 1 : 2
              }
            } 
            // 检查是否包含强调的标题文本
            else if (node.matches('p')) {
              const strongElement = node.querySelector('strong')
              const isTitle = strongElement && 
                            strongElement.textContent?.trim() === node.textContent?.trim() &&
                            !currentSection.content.trim()
              
              if (isTitle && strongElement?.textContent) {
                // 如果当前部分有内容，保存它
                if (currentSection.content.trim()) {
                  sections.push({ ...currentSection })
                }
                
                // 开始新的部分
                currentSection = {
                  title: strongElement.textContent.trim(),
                  content: '',
                  level: 2
                }
              } else {
                currentSection.content += node.outerHTML
              }
            } else {
              currentSection.content += node.outerHTML
            }
          } else if (node.textContent?.trim()) {
            currentSection.content += node.textContent
          }
        })
        
        // 添加最后一个部分
        if (currentSection.content.trim()) {
          sections.push(currentSection)
        }

        return { sections }
      }
    }
    
    // 如果无法解析HTML内容，则使用description创建一个基本的section
    return { 
      sections: [{
        title: 'About This Game',
        content: `<p>${game.description || 'No description available.'}</p>`,
        level: 1
      }]
    }
  }

  const toggleFullscreen = () => {
    const iframe = document.getElementById('gameFrame') as HTMLIFrameElement
    if (!iframe) return

    if (!isFullscreen) {
      if (iframe.requestFullscreen) {
        iframe.requestFullscreen()
      } else if ((iframe as any).webkitRequestFullscreen) {
        (iframe as any).webkitRequestFullscreen()
      } else if ((iframe as any).mozRequestFullScreen) {
        (iframe as any).mozRequestFullScreen()
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      } else if ((document as any).webkitExitFullscreen) {
        (document as any).webkitExitFullscreen()
      } else if ((document as any).mozCancelFullScreen) {
        (document as any).mozCancelFullScreen()
      }
    }
    
    setIsFullscreen(!isFullscreen)
  }

  const gameContent = parseGameContent(game.html_content)

  const renderSection = (section: Section) => {
    const titleClassName = section.level === 1
      ? "text-2xl font-bold text-white mb-6 pb-2 border-b border-gray-700"
      : "text-xl font-bold text-white mb-4"

    return (
      <div key={section.title} className="mb-8 last:mb-0">
        <h2 className={titleClassName}>{section.title}</h2>
        <div 
          className="text-gray-300 space-y-4 prose prose-invert max-w-none
            prose-headings:text-xl prose-headings:font-bold prose-headings:text-white prose-headings:mt-8 prose-headings:mb-4
            prose-p:text-gray-300 prose-p:leading-relaxed
            prose-strong:text-white
            prose-ul:list-disc prose-ul:pl-6 prose-ul:my-4
            prose-li:text-gray-300"
          dangerouslySetInnerHTML={{ __html: section.content }}
        />
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={onBack}
            className="text-gray-400 hover:text-white"
          >
            <ArrowLeft className="h-6 w-6" />
          </Button>
          <h1 className="text-2xl font-bold text-white">{game.title}</h1>
        </div>
        <Button
          variant="outline"
          onClick={toggleFullscreen}
          className="flex items-center gap-2"
        >
          <Maximize className="h-4 w-4" />
          <span>Fullscreen</span>
        </Button>
      </div>

      <div className="bg-gray-800 rounded-lg overflow-hidden mb-8">
        <div className="relative aspect-video">
          <iframe
            id="gameFrame"
            src={game.iframe_url}
            className="absolute inset-0 w-full h-full"
            frameBorder="0"
            allowFullScreen
          />
        </div>
      </div>

      <div className="prose prose-invert max-w-none">
        <div className="bg-gray-800 rounded-lg p-6 space-y-8">
          {gameContent.sections.map((section) => renderSection(section))}
        </div>
      </div>
    </div>
  )
} 