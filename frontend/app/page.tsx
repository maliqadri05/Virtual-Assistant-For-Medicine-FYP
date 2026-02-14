'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen px-4">
      <div className="max-w-2xl w-full text-center">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold text-medical-primary mb-4">
            MedAI Assistant
          </h1>
          <p className="text-xl text-slate-600">
            AI-Powered Medical Consultation and Diagnostic Assistance
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div className="text-3xl mb-3">🏥</div>
            <h3 className="font-semibold text-lg mb-2">Professional Assessment</h3>
            <p className="text-slate-600 text-sm">
              Get AI-powered medical assessments based on your symptoms
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div className="text-3xl mb-3">📋</div>
            <h3 className="font-semibold text-lg mb-2">Detailed Reports</h3>
            <p className="text-slate-600 text-sm">
              Receive comprehensive medical reports you can share with your doctor
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div className="text-3xl mb-3">💬</div>
            <h3 className="font-semibold text-lg mb-2">Smart Questions</h3>
            <p className="text-slate-600 text-sm">
              Dynamic follow-up questions for better diagnosis accuracy
            </p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center flex-wrap">
          <Link
            href="/chat/new"
            className="btn-primary text-center px-8 py-3 text-lg font-semibold"
          >
            Start Consultation
          </Link>
          <Link
            href="/dashboard"
            className="btn-secondary text-center px-8 py-3 text-lg font-semibold"
          >
            View History
          </Link>
          <Link
            href="/reports"
            className="bg-slate-400 hover:bg-slate-500 text-white text-center px-8 py-3 text-lg font-semibold rounded transition-colors"
          >
            My Reports
          </Link>
        </div>

        {/* Disclaimer */}
        <div className="mt-12 p-6 bg-yellow-50 border-l-4 border-yellow-400 rounded">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ Disclaimer:</strong> This is an AI-powered assistant and not
            a substitute for professional medical advice. Always consult with a
            licensed healthcare provider for diagnosis and treatment.
          </p>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-slate-500 text-sm">
          <p>Powered by MedGemma AI • Phase 2 Frontend</p>
        </div>
      </div>
    </main>
  );
}
