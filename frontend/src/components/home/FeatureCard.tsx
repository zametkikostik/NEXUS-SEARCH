import { LucideIcon } from 'lucide-react'

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
}

export default function FeatureCard({ icon: Icon, title, description }: FeatureCardProps) {
  return (
    <div className="card hover:border-nexus-500/50 transition-colors group">
      <div className="w-12 h-12 rounded-lg bg-nexus-500/10 flex items-center justify-center mb-4 group-hover:bg-nexus-500/20 transition-colors">
        <Icon className="w-6 h-6 text-nexus-400" />
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}
