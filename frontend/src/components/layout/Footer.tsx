import Link from 'next/link'
import { Github, Twitter, MessageCircle } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="border-t border-dark-border py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-lg font-bold gradient-text mb-4">NEXUS Search</h3>
            <p className="text-gray-400 text-sm">
              Децентрализованная поисковая система с Web3 и IPFS
            </p>
          </div>
          
          {/* Links */}
          <div>
            <h4 className="font-semibold mb-4">Продукт</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/search" className="hover:text-white">Поиск</Link></li>
              <li><Link href="/token" className="hover:text-white">Токен NXS</Link></li>
              <li><Link href="/staking" className="hover:text-white">Стейкинг</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Ресурсы</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/docs" className="hover:text-white">Документация</Link></li>
              <li><Link href="/api" className="hover:text-white">API</Link></li>
              <li><Link href="/github" className="hover:text-white">GitHub</Link></li>
            </ul>
          </div>
          
          {/* Social */}
          <div>
            <h4 className="font-semibold mb-4">Сообщество</h4>
            <div className="flex gap-4">
              <a href="https://github.com" className="text-gray-400 hover:text-white">
                <Github className="w-5 h-5" />
              </a>
              <a href="https://twitter.com" className="text-gray-400 hover:text-white">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="https://discord.com" className="text-gray-400 hover:text-white">
                <MessageCircle className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-dark-border text-center text-sm text-gray-500">
          <p>© 2024 NEXUS Search. MIT License.</p>
        </div>
      </div>
    </footer>
  )
}
