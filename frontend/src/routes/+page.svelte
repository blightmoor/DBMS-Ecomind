<script>
  import { Zap, Leaf, Globe, Brain, Shield, BarChart3, ArrowRight, Linkedin, Github, Instagram } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import overviewImage from '$lib/assets/overview.jpeg';

  function handleLogin() {
    goto('/login');
  }

  function handleSignup() {
    goto('/signup');
  }
</script>

<svelte:head>
  <title>AI Powered Carbon FootPrint - Overview</title>
  <meta name="description" content="Track and reduce your carbon footprint with AI-powered insights" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-green-50 to-lime-100">
  <!-- Navigation Bar -->
  <nav class="w-full h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-8 shadow-sm sticky top-0 z-50">
    <!-- Logo and App Name -->
			<div class="flex items-center gap-3 cursor-pointer" role="button" tabindex="0" on:click={goHome} on:keypress={(e) => e.key === 'Enter' && goHome()}>
				<div class="w-8 h-8 bg-gradient-to-br from-green-600 to-teal-600 rounded-lg flex items-center justify-center">
					<Leaf class="w-5 h-5 text-white" />
				</div>
				<div class="flex items-center gap-2">
          <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@600&display=swap" rel="stylesheet">

          <span class="text-xl font-semibold bg-gradient-to-r from-green-700 to-teal-700 bg-clip-text text-transparent" style="font-family:'Quicksand', sans-serif;">
            EcoMind
          </span>
				</div>
			</div>

    <!-- Action Buttons -->
    <div class="flex items-center gap-2 sm:gap-4">
      <button on:click={handleSignup} class="px-4 sm:px-6 py-2 rounded-lg font-medium text-xs sm:text-sm cursor-pointer transition-all duration-200 bg-transparent text-green-600 border border-green-600 hover:bg-green-50 hover:-translate-y-0.5">
        Sign Up
      </button>
      <button on:click={handleLogin} class="px-4 sm:px-6 py-2 rounded-lg font-medium text-xs sm:text-sm cursor-pointer transition-all duration-200 bg-green-600 text-white hover:bg-green-700 hover:-translate-y-0.5">
        Login
      </button>
    </div>
  </nav>

  <!-- Main Content -->
  <main class="py-4 sm:py-8 px-4 sm:px-8 max-w-6xl mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center min-h-[calc(100vh-8rem)] text-center lg:text-left">
      <!-- Left Side - Text Content -->
      <div class="flex flex-col gap-6 order-2 lg:order-1">
        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-800 leading-tight bg-gradient-to-r from-green-600 to-green-400 bg-clip-text text-transparent">
          Track Your Impact, Shape Your Future
        </h1>
        <p class="text-base sm:text-lg text-gray-600 leading-relaxed">
          Our AI-powered platform helps you monitor and reduce your carbon footprint through intelligent tracking and personalized recommendations.
        </p>
        <p class="text-base sm:text-lg text-gray-600 leading-relaxed">
          Join thousands of users who are making a difference by understanding their environmental impact and taking actionable steps towards a more sustainable lifestyle.
        </p>
      </div>

      <!-- Right Side - Image -->
      <div class="flex justify-center items-center order-1 lg:order-2">
        <img 
          src={overviewImage} 
          alt="Carbon footprint tracking dashboard" 
          class="w-full max-w-xs sm:max-w-lg h-auto rounded-2xl shadow-2xl"
        />
      </div>
    </div>
  </main>

  <!-- Features Section -->
  <section class="py-16 px-4 sm:px-8 bg-white">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-800 mb-4">
          Powerful Features for Sustainable Living
        </h2>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto">
          Our comprehensive platform provides everything you need to understand and reduce your environmental impact
        </p>
      </div>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        <!-- Real-Time Monitoring -->
        <div class="group bg-gradient-to-br from-green-50 to-green-100 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2 text-center">
          <div class="w-16 h-16 bg-green-600 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
            <Globe class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-3">Real-Time Emission Monitoring</h3>
          <p class="text-gray-600 leading-relaxed">
            Track your carbon emissions instantly across all daily activities with accurate real-time data collection and analysis
          </p>
        </div>

        <!-- AI Insights -->
        <div class="group bg-gradient-to-br from-blue-50 to-blue-100 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2 text-center">
          <div class="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
            <Brain class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-3">AI Insights & Forecasting</h3>
          <p class="text-gray-600 leading-relaxed">
            Get personalized recommendations and future emission predictions powered by advanced machine learning algorithms
          </p>
        </div>

        <!-- Blockchain Transparency -->
        <div class="group bg-gradient-to-br from-purple-50 to-purple-100 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2 text-center">
          <div class="w-16 h-16 bg-purple-600 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
            <Shield class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-3">Blockchain Transparency</h3>
          <p class="text-gray-600 leading-relaxed">
            Ensure data integrity and transparency with blockchain-backed verification of your sustainability achievements
          </p>
        </div>

        <!-- Smart Analytics -->
        <div class="group bg-gradient-to-br from-orange-50 to-orange-100 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2 text-center">
          <div class="w-16 h-16 bg-orange-600 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
            <BarChart3 class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-3">Smart Analytics Dashboard</h3>
          <p class="text-gray-600 leading-relaxed">
            Visualize your progress with interactive charts, detailed reports, and comprehensive sustainability metrics
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- How It Works Section -->
  <section class="py-16 px-4 sm:px-8 bg-gradient-to-br from-gray-50 to-gray-100">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-800 mb-4">
          How It Works
        </h2>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto">
          Get started with your sustainability journey in just four simple steps
        </p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8 relative">
        <!-- Connecting Line (Hidden on Mobile) -->
        <div class="hidden md:block absolute top-20 left-1/2 transform -translate-x-1/2 w-3/4 h-0.5 bg-gradient-to-r from-green-300 via-blue-300 via-purple-300 to-orange-300"></div>
        
        <!-- Step 1: Input Data -->
        <div class="relative text-center">
          <div class="w-20 h-20 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl relative z-10">
            <span class="text-2xl font-bold text-white">1</span>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-3">Input Data</h3>
          <p class="text-gray-600 leading-relaxed">
            Enter your daily activities, travel patterns, and energy consumption data through our intuitive interface
          </p>
        </div>

        <!-- Step 2: AI Analysis -->
        <div class="relative text-center">
          <div class="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl relative z-10">
            <span class="text-2xl font-bold text-white">2</span>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-3">AI Analysis</h3>
          <p class="text-gray-600 leading-relaxed">
            Our advanced AI algorithms process your data to calculate accurate carbon emissions and identify patterns
          </p>
        </div>

        <!-- Step 3: Get Recommendations -->
        <div class="relative text-center">
          <div class="w-20 h-20 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl relative z-10">
            <span class="text-2xl font-bold text-white">3</span>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-3">Get Recommendations</h3>
          <p class="text-gray-600 leading-relaxed">
            Receive personalized suggestions and actionable insights to reduce your environmental impact effectively
          </p>
        </div>

        <!-- Step 4: Track Progress -->
        <div class="relative text-center">
          <div class="w-20 h-20 bg-orange-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl relative z-10">
            <span class="text-2xl font-bold text-white">4</span>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-3">Track Progress</h3>
          <p class="text-gray-600 leading-relaxed">
            Monitor your sustainability journey with detailed analytics and celebrate your positive environmental impact
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Call-to-Action Section -->
  <section class="py-20 px-4 sm:px-8 bg-gradient-to-br from-green-100 via-white to-lime-50">
    <div class="max-w-4xl mx-auto text-center">
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-800 mb-6 leading-tight">
        Join thousands making sustainability <span class="bg-gradient-to-r from-green-600 to-green-400 bg-clip-text text-transparent">measurable</span>
      </h2>
      <p class="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
        Take the first step towards a more sustainable future. Start tracking your carbon footprint today and make a real difference.
      </p>
      <button 
        on:click={handleSignup}
        class="inline-flex items-center gap-3 bg-green-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:bg-green-700 hover:-translate-y-1 transition-all duration-300 shadow-xl hover:shadow-2xl"
      >
        Create Your Free Account
        <ArrowRight class="w-6 h-6" />
      </button>
      <p class="text-sm text-gray-500 mt-4">
        No credit card required • Free forever • Get started in 2 minutes
      </p>
    </div>
  </section>

  <!-- Footer -->
  <footer class="bg-gray-900 text-white py-12 px-4 sm:px-8">
    <div class="max-w-6xl mx-auto">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Logo and Description -->
        <div class="text-center md:text-left">
          <div class="flex items-center gap-3 cursor-pointer" role="button" tabindex="0" on:click={goHome} on:keypress={(e) => e.key === 'Enter' && goHome()}>
            <div class="w-8 h-8 bg-gradient-to-br from-green-600 to-teal-600 rounded-lg flex items-center justify-center">
              <Leaf class="w-5 h-5 text-white" />
            </div>
            <div class="flex items-center gap-2">
              <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@600&display=swap" rel="stylesheet">

              <span class="text-xl font-semibold bg-gradient-to-r from-green-700 to-teal-700 bg-clip-text text-transparent" style="font-family:'Quicksand', sans-serif;">
                EcoMind
              </span>
            </div>
          </div>
          <p class="text-gray-400 leading-relaxed">
            Empowering individuals and organizations to make data-driven decisions for a sustainable future through AI-powered carbon footprint tracking.
          </p>
        </div>

        <!-- Quick Links -->
        <div class="text-center">
          <h3 class="text-lg font-bold mb-4">Quick Links</h3>
          <div class="space-y-2">
            <a href="/" class="block text-gray-400 hover:text-white transition-colors">Home</a>
            <a href="/about" class="block text-gray-400 hover:text-white transition-colors">About</a>
            <a href="/contact" class="block text-gray-400 hover:text-white transition-colors">Contact</a>
            <a href="/privacy" class="block text-gray-400 hover:text-white transition-colors">Privacy Policy</a>
          </div>
        </div>

        <!-- Social Media -->
        <div class="text-center md:text-right">
          <h3 class="text-lg font-bold mb-4">Follow Us</h3>
          <div class="flex justify-center md:justify-end gap-4 mb-4">
            <a href="#" class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-green-600 transition-colors">
              <Linkedin class="w-5 h-5" />
            </a>
            <a href="#" class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-green-600 transition-colors">
              <Github class="w-5 h-5" />
            </a>
            <a href="#" class="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-green-600 transition-colors">
              <Instagram class="w-5 h-5" />
            </a>
          </div>
          <p class="text-sm text-gray-400">
            Stay updated with our latest features and sustainability tips
          </p>
        </div>
      </div>

      <!-- Copyright -->
      <div class="border-t border-gray-800 mt-8 pt-8 text-center">
        <p class="text-gray-400 text-sm">
          © 2025 Smart Carbon System. All rights reserved. | Making sustainability measurable for everyone.
        </p>
      </div>
    </div>
  </footer>
</div>

