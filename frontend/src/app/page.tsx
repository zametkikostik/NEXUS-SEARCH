'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Shield, Zap, Globe, Lock, Database } from 'lucide-react'
import Header from '@components/layout/Header'
import Footer from '@components/layout/Footer'
import SearchBar from '@components/search/SearchBar'
import FeatureCard from '@components/home/FeatureCard'

export default function Home() {
  const features = [
    {
      icon: Shield,
      title: 'Privacy-First',
      description: 'Никаких логов, никакого трекинга. Ваши поисковые запросы остаются приватными.'
    },
    {
      icon: Globe,
      title: 'Децентрализация',
      description: 'Работает на распределённой сети узлов без единой точки отказа.'
    },
    {
      icon: Lock,
      title: 'Web3 Аутентификация',
      description: 'Вход через криптокошелёк. Никаких паролей или email.'
    },
    {
      icon: Database,
      title: 'IPFS Хранение',
      description: 'Результаты поиска хранятся в децентрализованной сети IPFS.'
    },
    {
      icon: Zap,
      title: 'Анти-Бан Система',
      description: 'Обход блокировок с помощью ротации прокси и умных алгоритмов.'
    },
    {
      icon: Globe,
      title: 'Токеномика',
      description: 'Зарабатывайте NXS токены за поиск и стейкинг.'
    }
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 px-4 overflow-hidden">
          {/* Background Effects */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-40 -right-40 w-80 h-80 bg-nexus-500/20 rounded-full blur-3xl" />
            <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-nexus-600/20 rounded-full blur-3xl" />
          </div>
          
          <div className="relative max-w-6xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-5xl md:text-7xl font-bold mb-6">
                <span className="gradient-text">NEXUS Search</span>
              </h1>
              <p className="text-xl md:text-2xl text-gray-400 mb-8 max-w-3xl mx-auto">
                Децентрализованная поисковая система нового поколения с Web3, 
                IPFS и полной приватностью
              </p>
            </motion.div>
            
            {/* Search Bar */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="max-w-3xl mx-auto mb-12"
            >
              <SearchBar />
            </motion.div>
            
            {/* Stats */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="flex flex-wrap justify-center gap-8 text-sm text-gray-500"
            >
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-nexus-400" />
                <span>100% Приватно</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-nexus-400" />
                <span>6+ Провайдеров</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-nexus-400" />
                <span>Мгновенный Поиск</span>
              </div>
            </motion.div>
          </div>
        </section>
        
        {/* Features Section */}
        <section className="py-20 px-4 bg-dark-card/50">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Почему <span className="gradient-text">NEXUS</span>?
              </h2>
              <p className="text-gray-400 max-w-2xl mx-auto">
                Мы объединили лучшие технологии для создания поисковой системы будущего
              </p>
            </motion.div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <FeatureCard {...feature} />
                </motion.div>
              ))}
            </div>
          </div>
        </section>
        
        {/* How It Works Section */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Как это <span className="gradient-text">работает</span>?
              </h2>
            </motion.div>
            
            <div className="grid md:grid-cols-4 gap-8">
              {[
                { step: '01', title: 'Подключите кошелёк', desc: 'MetaMask или любой Web3 кошелёк' },
                { step: '02', title: 'Введите запрос', desc: 'Поиск по множеству источников' },
                { step: '03', title: 'Получите результаты', desc: 'Агрегация из 6+ провайдеров' },
                { step: '04', title: 'Заработайте токены', desc: 'NXS rewards за активность' },
              ].map((item, index) => (
                <motion.div
                  key={item.step}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className="text-center"
                >
                  <div className="text-5xl font-bold gradient-text mb-4">{item.step}</div>
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  <p className="text-gray-400">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  )
}
