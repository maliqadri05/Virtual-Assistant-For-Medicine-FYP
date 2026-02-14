'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

export default function Home() {
  const [showVideoModal, setShowVideoModal] = useState(false);
  const { isAuthenticated, logout, isLoading } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <main className="bg-gray-50">
      {/* Navigation */}
      <nav className="fixed w-full bg-white/80 backdrop-blur-md z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
                <svg
                  className="w-7 h-7 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                MedAI Assistant
              </span>
            </Link>

            <div className="hidden md:flex items-center space-x-8">
              <a
                href="#features"
                className="text-gray-700 hover:text-indigo-600 font-medium transition"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                className="text-gray-700 hover:text-indigo-600 font-medium transition"
              >
                How It Works
              </a>
              <a
                href="#technology"
                className="text-gray-700 hover:text-indigo-600 font-medium transition"
              >
                Technology
              </a>
              <a
                href="#demo"
                className="text-gray-700 hover:text-indigo-600 font-medium transition"
              >
                Demo
              </a>
            </div>

            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <Link
                    href="/dashboard"
                    className="hidden md:block px-6 py-2.5 text-gray-700 font-medium hover:text-indigo-600 transition"
                  >
                    Dashboard
                  </Link>
                  <button
                    onClick={handleLogout}
                    disabled={isLoading}
                    className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transform hover:scale-105 transition disabled:opacity-50"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/auth/login"
                    className="hidden md:block px-6 py-2.5 text-gray-700 font-medium hover:text-indigo-600 transition"
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/auth/register"
                    className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transform hover:scale-105 transition"
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="inline-block px-4 py-2 bg-indigo-100 text-indigo-700 rounded-full text-sm font-semibold">
                🚀 AI-Powered Medical Diagnostics
              </div>

              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Your Intelligent{' '}
                <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Medical Assistant
                </span>
              </h1>

              <p className="text-xl text-gray-600 leading-relaxed">
                Harness the power of advanced AI to analyze medical images, process patient histories, and generate comprehensive diagnostic reports in seconds.
              </p>

              <div className="flex flex-wrap gap-4">
                <Link
                  href="/chat/new"
                  className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition"
                >
                  Try Live Demo
                </Link>
                <button
                  onClick={() => setShowVideoModal(true)}
                  className="px-8 py-4 bg-white text-gray-700 rounded-xl font-semibold text-lg border-2 border-gray-200 hover:border-indigo-600 transition"
                >
                  Watch Demo
                </button>
              </div>

              <div className="flex items-center space-x-8 pt-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">95%</div>
                  <div className="text-sm text-gray-600">Accuracy Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">&lt;30s</div>
                  <div className="text-sm text-gray-600">Report Time</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">24/7</div>
                  <div className="text-sm text-gray-600">Available</div>
                </div>
              </div>
            </div>

            <div className="relative animate-float">
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-600 opacity-20 blur-3xl rounded-full"></div>
              <div className="relative z-10 w-full h-96 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl shadow-2xl flex items-center justify-center">
                <div className="text-center">
                  <div className="text-7xl mb-4">🏥</div>
                  <p className="text-gray-600 font-semibold">Medical AI</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Healthcare
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need for intelligent medical diagnostics
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: '🖼️',
                title: 'Medical Image Analysis',
                description:
                  'Advanced AI analyzes X-rays, CT scans, and MRIs with exceptional accuracy. Supports DICOM format and automatic PHI removal.',
              },
              {
                icon: '💬',
                title: 'Conversational Interface',
                description:
                  'Natural language interaction with multi-agent AI system. Text and voice input supported for seamless patient interaction.',
              },
              {
                icon: '📄',
                title: 'Instant Report Generation',
                description:
                  'Comprehensive diagnostic reports in seconds. Key findings, analysis, recommendations, and downloadable PDFs.',
              },
              {
                icon: '👤',
                title: 'Patient History Integration',
                description:
                  'Complete patient profiles with age, sex, weight, medical history. AI considers full context for accurate diagnosis.',
              },
              {
                icon: '🔒',
                title: 'HIPAA-Compliant Security',
                description:
                  'End-to-end encryption, secure authentication, and complete audit trails. Your patient data is always protected.',
              },
              {
                icon: '🤖',
                title: 'Multi-Agent AI System',
                description:
                  'Intelligent agent architecture with validation, questioning, and diagnostic capabilities.',
              },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="feature-card bg-white p-8 rounded-2xl shadow-lg border border-gray-100 hover:shadow-2xl hover:-translate-y-2 transition"
              >
                <div className="w-14 h-14 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center mb-6 text-2xl">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
            <p className="text-xl text-gray-600">
              Simple, fast, and accurate diagnostic process
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { num: 1, title: 'Upload Images', desc: 'Upload X-rays, CT scans, or MRIs. Supports DICOM and standard image formats.' },
              { num: 2, title: 'Provide Details', desc: 'Share patient history via text or voice. AI asks intelligent follow-up questions.' },
              { num: 3, title: 'AI Analysis', desc: 'MedGemma analyzes images and context using advanced medical AI models.' },
              { num: 4, title: 'Get Report', desc: 'Receive comprehensive diagnostic report with findings and recommendations.' },
            ].map((step) => (
              <div key={step.num} className="text-center">
                <div className="w-20 h-20 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-3xl font-bold">
                  {step.num}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{step.title}</h3>
                <p className="text-gray-600">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section id="technology" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Powered by Cutting-Edge Technology
            </h2>
            <p className="text-xl text-gray-600">
              Built on the most advanced AI and medical imaging technologies
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                emoji: '🧠',
                title: 'MedGemma AI',
                description: 'Google\'s specialized medical AI model trained on vast medical datasets for accurate diagnosis.',
                tags: ['4B Parameters', 'Multimodal'],
              },
              {
                emoji: '🔬',
                title: 'DICOM Processing',
                description: 'Industry-standard medical imaging format with automatic PHI removal and de-identification.',
                tags: ['Secure', 'Compliant'],
              },
              {
                emoji: '🎯',
                title: 'Multi-Agent System',
                description: 'Intelligent agent architecture with validation, questioning, and diagnostic capabilities.',
                tags: ['Adaptive', 'Precise'],
              },
            ].map((tech, idx) => (
              <div
                key={idx}
                className="bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-2xl border border-indigo-200"
              >
                <div className="text-4xl mb-4">{tech.emoji}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{tech.title}</h3>
                <p className="text-gray-600 mb-4">{tech.description}</p>
                <div className="flex flex-wrap gap-2">
                  {tech.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-white text-indigo-700 rounded-full text-sm font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Demo */}
      <section id="demo" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Try It Yourself</h2>
            <p className="text-xl text-gray-600">
              Experience the power of AI-assisted diagnostics
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="grid lg:grid-cols-2">
              {/* Left: Upload & Input */}
              <div className="p-8 border-r border-gray-200">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">
                  Patient Information
                </h3>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Patient Details
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      <input
                        type="text"
                        placeholder="Age"
                        className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                      />
                      <select className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none">
                        <option>Male</option>
                        <option>Female</option>
                        <option>Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Describe Symptoms
                    </label>
                    <textarea
                      rows={4}
                      placeholder="Tell us about the symptoms, their duration, and severity..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none"
                    ></textarea>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Upload Medical Images
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition cursor-pointer">
                      <svg
                        className="w-12 h-12 text-gray-400 mx-auto mb-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                      <p className="text-sm text-gray-600 font-medium">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        X-ray, CT, MRI • DICOM or PNG/JPEG
                      </p>
                    </div>
                  </div>

                  <Link
                    href="/chat/new"
                    className="w-full px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold text-lg hover:shadow-lg transform hover:scale-105 transition text-center"
                  >
                    Generate Diagnostic Report
                  </Link>
                </div>
              </div>

              {/* Right: Results */}
              <div className="p-8 bg-gray-50">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">
                  AI Analysis Results
                </h3>

                <div className="space-y-6">
                  <div className="bg-white p-6 rounded-xl border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-bold text-gray-900">Processing Status</h4>
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                        Ready
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      Upload patient information and medical images to begin AI
                      analysis...
                    </p>
                  </div>

                  <div className="bg-white p-6 rounded-xl border border-gray-200 opacity-50">
                    <h4 className="font-bold text-gray-900 mb-3">Key Findings</h4>
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-full"></div>
                      <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-xl border border-gray-200 opacity-50">
                    <h4 className="font-bold text-gray-900 mb-3">
                      Recommendations
                    </h4>
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-full"></div>
                      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                    </div>
                  </div>

                  <div className="bg-indigo-50 border-2 border-indigo-200 p-6 rounded-xl">
                    <div className="flex items-start space-x-3">
                      <svg
                        className="w-6 h-6 text-indigo-600 flex-shrink-0 mt-0.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <div>
                        <p className="text-sm font-semibold text-indigo-900 mb-1">
                          Important Note
                        </p>
                        <p className="text-sm text-indigo-800">
                          This is an AI-assisted tool. Always consult with qualified
                          healthcare professionals for diagnosis and treatment.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Healthcare?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Join leading medical professionals using AI-powered diagnostics
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/chat/new"
              className="px-8 py-4 bg-white text-indigo-600 rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition"
            >
              Start Now
            </Link>
            <Link
              href="/dashboard"
              className="px-8 py-4 border-2 border-white text-white rounded-xl font-semibold text-lg hover:bg-white/10 transition"
            >
              View Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Video Modal */}
      {showVideoModal && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setShowVideoModal(false)}
        >
          <div
            className="bg-white rounded-lg max-w-2xl w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold text-gray-900">Product Demo</h3>
              <button
                onClick={() => setShowVideoModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="aspect-video bg-gray-200 rounded-lg flex items-center justify-center">
              <p className="text-gray-600">Video player would go here</p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
