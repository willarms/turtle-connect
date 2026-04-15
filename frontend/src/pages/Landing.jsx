import { Link } from 'react-router-dom'

const HOW_IT_WORKS = [
  { icon: '🌱', title: 'Share Your Interests', desc: 'Tell us what you love—from gardening to movies, crafts, and more.' },
  { icon: '🤝', title: 'Get Matched', desc: 'Our AI finds groups of people who share your passions.' },
  { icon: '📞', title: 'Connect & Chat', desc: 'Join simple phone or video calls with your groups.' },
  { icon: '🛡️', title: 'Safe & Simple', desc: 'Easy to use interface designed with seniors in mind.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-[var(--turtle-bg)]">
      {/* Hero */}
      <div className="max-w-5xl mx-auto px-6 py-16 flex flex-col md:flex-row items-center gap-12">
        <div className="flex-1">
          <p className="text-[var(--turtle-green)] text-sm font-medium mb-3">Connect at Your Own Pace</p>
          <h1 className="text-4xl md:text-5xl font-bold text-[var(--turtle-text)] leading-tight mb-4">
            Find Your Community
          </h1>
          <p className="text-[var(--turtle-text-muted)] text-lg mb-8 leading-relaxed">
            Turtle uses smart matching to connect you with others who share your
            interests—from gardening to crocheting to fishing and favorite films. Join
            groups, make friends, and enjoy activities together.
          </p>
          <div className="flex gap-4 flex-wrap">
            <Link
              to="/login"
              className="px-6 py-3 bg-[var(--turtle-green)] text-white rounded-md font-medium hover:bg-[var(--turtle-green-dark)] transition-colors"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="px-6 py-3 border border-gray-300 rounded-md text-[var(--turtle-text)] font-medium hover:border-[var(--turtle-green)] transition-colors"
            >
              Browse Groups
            </Link>
          </div>
        </div>
        <div className="flex-shrink-0 w-56 h-56 bg-[var(--turtle-green-light)] rounded-2xl flex items-center justify-center">
          <span className="text-8xl">🐢</span>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-white py-16">
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-center text-2xl font-semibold text-[var(--turtle-text)] mb-10">
            How It Works
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {HOW_IT_WORKS.map(item => (
              <div key={item.title} className="text-center p-4 border border-[var(--turtle-border)] rounded-xl">
                <div className="text-3xl mb-3">{item.icon}</div>
                <h3 className="font-semibold text-[var(--turtle-text)] mb-2 text-sm">{item.title}</h3>
                <p className="text-[var(--turtle-text-muted)] text-xs leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="bg-[var(--turtle-green-light)] py-16 text-center">
        <h2 className="text-2xl font-semibold text-[var(--turtle-text)] mb-3">
          Ready to Make New Friends?
        </h2>
        <p className="text-[var(--turtle-text-muted)] mb-6">
          Join Turtle today and discover a community that shares your interests. It's never too late
          to make meaningful connections.
        </p>
        <Link
          to="/login"
          className="px-8 py-3 bg-[var(--turtle-green)] text-white rounded-md font-medium hover:bg-[var(--turtle-green-dark)] transition-colors"
        >
          Create Your Profile
        </Link>
      </div>
    </div>
  )
}
