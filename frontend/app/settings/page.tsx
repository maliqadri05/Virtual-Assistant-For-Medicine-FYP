'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/ProtectedRoute';

interface Settings {
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  privacy: {
    shareWithDoctors: boolean;
    shareWithResearch: boolean;
    anonymousData: boolean;
  };
  preferences: {
    language: string;
    theme: string;
    timezone: string;
  };
  security: {
    twoFactor: boolean;
    sessionTimeout: string;
  };
}

function SettingsContent() {
  const [settings, setSettings] = useState<Settings>({
    notifications: {
      email: true,
      push: true,
      sms: false,
    },
    privacy: {
      shareWithDoctors: true,
      shareWithResearch: false,
      anonymousData: true,
    },
    preferences: {
      language: 'en',
      theme: 'light',
      timezone: 'America/New_York',
    },
    security: {
      twoFactor: false,
      sessionTimeout: '30',
    },
  });

  const [successMessage, setSuccessMessage] = useState('');
  const [unsavedChanges, setUnsavedChanges] = useState(false);

  const handleToggle = (section: keyof Settings, field: string, value: boolean) => {
    setSettings((prev) => ({
      ...prev,
      [section]: {
        ...(prev[section] as Record<string, boolean | string>),
        [field]: value,
      },
    }));
    setUnsavedChanges(true);
  };

  const handleChange = (section: keyof Settings, field: string, value: string) => {
    setSettings((prev) => ({
      ...prev,
      [section]: {
        ...(prev[section] as Record<string, boolean | string>),
        [field]: value,
      },
    }));
    setUnsavedChanges(true);
  };

  const handleSave = () => {
    setSuccessMessage('Settings saved successfully!');
    setUnsavedChanges(false);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const handleCancel = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">Settings</h1>
              <p className="text-indigo-100 mt-2">Manage your preferences and account settings</p>
            </div>
            <Link
              href="/dashboard"
              className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-700 font-semibold">✓ {successMessage}</p>
          </div>
        )}

        {/* Unsaved Changes Warning */}
        {unsavedChanges && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-700 font-semibold">
              ⚠️ You have unsaved changes. Don't forget to save!
            </p>
          </div>
        )}

        {/* Settings Sections */}
        <div className="space-y-6">
          {/* Notification Settings */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="text-2xl mr-3">🔔</span>
              Notifications
            </h3>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-semibold text-gray-900">Email Notifications</h4>
                  <p className="text-sm text-gray-600">Receive updates via email</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications.email}
                    onChange={(e) =>
                      handleToggle('notifications', 'email', e.target.checked)
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>

              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-semibold text-gray-900">Push Notifications</h4>
                  <p className="text-sm text-gray-600">Receive push notifications on browser</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications.push}
                    onChange={(e) => handleToggle('notifications', 'push', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>

              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-semibold text-gray-900">SMS Alerts</h4>
                  <p className="text-sm text-gray-600">Receive urgent alerts via SMS</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications.sms}
                    onChange={(e) => handleToggle('notifications', 'sms', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Privacy Settings */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="text-2xl mr-3">🔒</span>
              Privacy & Data
            </h3>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-semibold text-gray-900">Share with Doctors</h4>
                  <p className="text-sm text-gray-600">Allow qualified doctors to access your data</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.privacy.shareWithDoctors}
                    onChange={(e) =>
                      handleToggle('privacy', 'shareWithDoctors', e.target.checked)
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>

              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-semibold text-gray-900">Share with Research</h4>
                  <p className="text-sm text-gray-600">Help improve AI models through anonymized data</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.privacy.shareWithResearch}
                    onChange={(e) =>
                      handleToggle('privacy', 'shareWithResearch', e.target.checked)
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>

              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-semibold text-gray-900">Anonymous Analytics</h4>
                  <p className="text-sm text-gray-600">Allow usage analytics for improvement</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.privacy.anonymousData}
                    onChange={(e) =>
                      handleToggle('privacy', 'anonymousData', e.target.checked)
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="text-2xl mr-3">⚙️</span>
              Preferences
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Language</label>
                <select
                  value={settings.preferences.language}
                  onChange={(e) => handleChange('preferences', 'language', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                  <option value="de">Deutsch</option>
                  <option value="zh">中文</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Theme</label>
                <select
                  value={settings.preferences.theme}
                  onChange={(e) => handleChange('preferences', 'theme', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto (System)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Timezone</label>
                <select
                  value={settings.preferences.timezone}
                  onChange={(e) => handleChange('preferences', 'timezone', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="America/New_York">EST (Eastern)</option>
                  <option value="America/Chicago">CST (Central)</option>
                  <option value="America/Denver">MST (Mountain)</option>
                  <option value="America/Los_Angeles">PST (Pacific)</option>
                  <option value="Europe/London">GMT (London)</option>
                  <option value="Europe/Paris">CET (Paris)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Security Settings */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="text-2xl mr-3">🛡️</span>
              Security
            </h3>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-semibold text-gray-900">Two-Factor Authentication</h4>
                  <p className="text-sm text-gray-600">Add extra security to your account</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.security.twoFactor}
                    onChange={(e) =>
                      handleToggle('security', 'twoFactor', e.target.checked)
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Session Timeout (minutes)
                </label>
                <select
                  value={settings.security.sessionTimeout}
                  onChange={(e) => handleChange('security', 'sessionTimeout', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="15">15 minutes</option>
                  <option value="30">30 minutes</option>
                  <option value="60">1 hour</option>
                  <option value="120">2 hours</option>
                  <option value="never">Never</option>
                </select>
              </div>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="bg-red-50 border-2 border-red-200 rounded-lg shadow-md p-8">
            <h3 className="text-2xl font-bold text-red-900 mb-6 flex items-center">
              <span className="text-2xl mr-3">⚠️</span>
              Danger Zone
            </h3>

            <div className="space-y-4">
              <button className="w-full px-6 py-3 bg-red-100 hover:bg-red-200 text-red-700 font-semibold rounded-lg transition">
                Change Password
              </button>
              <button className="w-full px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition">
                🗑️ Delete My Account
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-end">
            <button
              onClick={handleCancel}
              className="px-6 py-2 bg-gray-300 hover:bg-gray-400 text-gray-900 font-semibold rounded-lg transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition"
            >
              💾 Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}
