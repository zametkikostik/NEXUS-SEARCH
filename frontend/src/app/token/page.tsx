'use client'

import { motion } from 'framer-motion'
import { Coins, TrendingUp, Lock, Wallet, Shield, Globe } from 'lucide-react'
import Header from '@components/layout/Header'
import Footer from '@components/layout/Footer'

const tokenDistribution = [
  { category: 'Пользователи', percent: 30, color: 'from-nexus-400 to-nexus-500', desc: 'Rewards за поиск и стейкинг' },
  { category: 'Команда', percent: 20, color: 'from-purple-400 to-purple-500', desc: '4 года вестинга' },
  { category: 'Инвесторы', percent: 20, color: 'from-blue-400 to-blue-500', desc: '2 года вестинга' },
  { category: 'Экосистема', percent: 20, color: 'from-green-400 to-green-500', desc: 'Гранты, партнёрства' },
  { category: 'Ликвидность', percent: 10, color: 'from-orange-400 to-orange-500', desc: 'DEX листинги' },
]

const utilities = [
  { icon: Coins, title: 'Оплата поиска', desc: 'Pay-per-search модель с микроплатежами' },
  { icon: Lock, title: 'Подписка NFT', desc: 'Премиум функции через subscription NFT' },
  { icon: TrendingUp, title: 'Стейкинг', desc: 'Зарабатывайте до 5% APY на стейкинге' },
  { icon: Shield, title: 'DAO Управление', desc: 'Голосуйте за развитие платформы' },
]

export default function TokenPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 py-12 px-4">
        <div className="max-w-6xl mx-auto">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-nexus-400 to-nexus-600 flex items-center justify-center mx-auto mb-6">
              <Coins className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">NXS Token</span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Утилитарный токен экосистемы NEXUS Search
            </p>
          </motion.div>
          
          {/* Token Info */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card text-center"
            >
              <div className="text-3xl font-bold gradient-text mb-2">1,000,000,000</div>
              <div className="text-gray-400">Общий запас</div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card text-center"
            >
              <div className="text-3xl font-bold gradient-text mb-2">18</div>
              <div className="text-gray-400">Децималы</div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card text-center"
            >
              <div className="text-3xl font-bold gradient-text mb-2">ERC-20</div>
              <div className="text-gray-400">Стандарт</div>
            </motion.div>
          </div>
          
          {/* Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-16"
          >
            <h2 className="text-2xl font-bold mb-8 text-center">Распределение токенов</h2>
            
            <div className="grid md:grid-cols-5 gap-4">
              {tokenDistribution.map((item, index) => (
                <motion.div
                  key={item.category}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="card text-center"
                >
                  <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${item.color} mx-auto mb-4 flex items-center justify-center`}>
                    <span className="text-xl font-bold text-white">{item.percent}%</span>
                  </div>
                  <h3 className="font-semibold mb-2">{item.category}</h3>
                  <p className="text-sm text-gray-400">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
          
          {/* Utilities */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-2xl font-bold mb-8 text-center">Утилита токена</h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {utilities.map((item, index) => (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="card"
                >
                  <div className="w-12 h-12 rounded-lg bg-nexus-500/10 flex items-center justify-center mb-4">
                    <item.icon className="w-6 h-6 text-nexus-400" />
                  </div>
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-gray-400 text-sm">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
          
          {/* Contract Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-16 card"
          >
            <h2 className="text-2xl font-bold mb-6">Смарт-контракты</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-dark-card rounded-lg">
                <div className="flex items-center gap-3">
                  <Wallet className="w-5 h-5 text-nexus-400" />
                  <span>NXS Token</span>
                </div>
                <code className="text-sm text-gray-400">
                  {process.env.NEXT_PUBLIC_TOKEN_CONTRACT_ADDRESS || '0x...'}
                </code>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-dark-card rounded-lg">
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-nexus-400" />
                  <span>Staking Contract</span>
                </div>
                <code className="text-sm text-gray-400">
                  {process.env.NEXT_PUBLIC_STAKING_CONTRACT_ADDRESS || '0x...'}
                </code>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-dark-card rounded-lg">
                <div className="flex items-center gap-3">
                  <Lock className="w-5 h-5 text-nexus-400" />
                  <span>Subscription NFT</span>
                </div>
                <code className="text-sm text-gray-400">0x...</code>
              </div>
            </div>
          </motion.div>
        </div>
      </main>
      
      <Footer />
    </div>
  )
}
