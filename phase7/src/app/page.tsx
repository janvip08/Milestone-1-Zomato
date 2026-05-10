'use client'

import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()

  const handleGetStarted = () => {
    router.push('/preferences')
  }

  return (
    <div className="bg-surface text-on-surface min-h-screen">
      {/* TopAppBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-margin-mobile h-16 bg-surface">
        <div className="flex items-center">
          <span className="material-symbols-outlined text-on-surface-variant">menu</span>
        </div>
        <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-primary tracking-tight">CraveAI</h1>
        <div className="w-8 h-8 rounded-full bg-surface-variant overflow-hidden border border-outline-variant">
          <img 
            alt="User" 
            src="/api/placeholder/32/32"
            className="w-full h-full object-cover"
          />
        </div>
      </header>

      <main className="pt-20 px-margin-mobile max-w-container-max mx-auto">
        {/* Hero Section */}
        <section className="text-center py-xl">
          <div className="mb-lg">
            <span className="material-symbols-outlined text-primary text-6xl mb-md" style={{ fontVariationSettings: "'FILL' 1" }}>
              restaurant
            </span>
          </div>
          <h2 className="font-headline-xl text-headline-xl text-on-surface mb-md">
            Discover Your Perfect Bite
          </h2>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg mx-auto mb-xl">
            AI-powered restaurant recommendations tailored to your unique preferences, budget, and taste.
          </p>
          
          <button
            onClick={handleGetStarted}
            className="px-8 py-4 bg-primary text-on-primary rounded-xl font-headline-lg-mobile text-headline-lg-mobile shadow-lg shadow-primary/20 flex items-center justify-center gap-3 mx-auto active:scale-95 transition-transform"
          >
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
              auto_awesome
            </span>
            Get Started
          </button>
        </section>

        {/* Features Grid */}
        <section className="mb-xl">
          <h3 className="font-headline-lg text-headline-lg text-on-surface text-center mb-lg">
            Powered by Advanced AI
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
            <div className="bg-surface-container-low rounded-xl p-md text-center">
              <span className="material-symbols-outlined text-primary text-3xl mb-sm">psychology</span>
              <h4 className="font-title-md text-title-md text-on-surface mb-xs">Smart Preferences</h4>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Learns your taste patterns and dietary preferences over time
              </p>
            </div>
            
            <div className="bg-surface-container-low rounded-xl p-md text-center">
              <span className="material-symbols-outlined text-secondary text-3xl mb-sm">location_on</span>
              <h4 className="font-title-md text-title-md text-on-surface mb-xs">Multi-City Support</h4>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Optimized recommendations across multiple cities
              </p>
            </div>
            
            <div className="bg-surface-container-low rounded-xl p-md text-center">
              <span className="material-symbols-outlined text-tertiary text-3xl mb-sm">star</span>
              <h4 className="font-title-md text-title-md text-on-surface mb-xs">Hybrid Ranking</h4>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Combines AI, vector search, and traditional ranking
              </p>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="mb-xl">
          <h3 className="font-headline-lg text-headline-lg text-on-surface text-center mb-lg">
            How It Works
          </h3>
          <div className="space-y-lg">
            <div className="flex items-center gap-md">
              <div className="w-12 h-12 bg-primary text-on-primary rounded-full flex items-center justify-center font-title-md flex-shrink-0">
                1
              </div>
              <div>
                <h4 className="font-title-md text-title-md text-on-surface mb-xs">Set Your Preferences</h4>
                <p className="font-body-sm text-body-sm text-on-surface-variant">
                  Tell us about your budget, cuisine preferences, and dietary requirements
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-md">
              <div className="w-12 h-12 bg-primary text-on-primary rounded-full flex items-center justify-center font-title-md flex-shrink-0">
                2
              </div>
              <div>
                <h4 className="font-title-md text-title-md text-on-surface mb-xs">AI Analysis</h4>
                <p className="font-body-sm text-body-sm text-on-surface-variant">
                  Our AI analyzes thousands of restaurants to find your perfect matches
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-md">
              <div className="w-12 h-12 bg-primary text-on-primary rounded-full flex items-center justify-center font-title-md flex-shrink-0">
                3
              </div>
              <div>
                <h4 className="font-title-md text-title-md text-on-surface mb-xs">Get Recommendations</h4>
                <p className="font-body-sm text-body-sm text-on-surface-variant">
                  Receive personalized recommendations with AI match scores and insights
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center py-xl bg-primary-fixed rounded-xl ai-gradient-border">
          <span className="material-symbols-outlined text-primary text-4xl mb-md">rocket_launch</span>
          <h3 className="font-headline-lg text-headline-lg text-primary mb-xs">
            Ready to Discover?
          </h3>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg mx-auto mb-md">
            Join thousands of food lovers who have found their perfect restaurants with CraveAI
          </p>
          <button
            onClick={handleGetStarted}
            className="px-6 py-3 bg-primary text-on-primary rounded-xl font-body-lg font-bold active:scale-95 transition-transform"
          >
            Start Your Journey
          </button>
        </section>
      </main>
    </div>
  )
}
