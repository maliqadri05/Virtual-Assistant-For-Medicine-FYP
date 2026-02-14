/**
 * Mock API Service for Development
 * Simulates backend responses for testing and development without server
 */

import { RequestOptions } from './api';

/**
 * Mock Data Generator
 */
class MockDataGenerator {
  static generateConversationId(): string {
    return `conv-${Math.random().toString(36).substr(2, 9)}`;
  }

  static generateMessageId(): string {
    return `msg-${Math.random().toString(36).substr(2, 9)}`;
  }

  static generateReportId(): string {
    return `report-${Math.random().toString(36).substr(2, 9)}`;
  }

  static generateMockConversation(id: string = this.generateConversationId()) {
    return {
      id,
      title: 'Medical Consultation',
      createdAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date().toISOString(),
      status: 'completed',
      messages: [
        {
          id: this.generateMessageId(),
          role: 'user',
          content: 'I have been experiencing persistent headaches for the past week.',
          timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
        },
        {
          id: this.generateMessageId(),
          role: 'assistant',
          content: 'I understand. Persistent headaches can have various causes. Could you describe the type of pain?',
          timestamp: new Date(Date.now() - 9 * 60 * 1000).toISOString(),
        },
      ],
      patientContext: {
        age: 35,
        gender: 'M',
        medicalHistory: ['migraine', 'hypertension'],
      },
    };
  }

  static generateMockReport(id: string = this.generateReportId()) {
    return {
      id,
      conversationId: this.generateConversationId(),
      title: 'Medical Report - Headache Assessment',
      createdAt: new Date().toISOString(),
      findings: 'Patient presents with persistent headaches lasting one week. Physical examination unremarkable.',
      diagnosis: 'Tension headache with mild hypertension component',
      recommendations: [
        'Rest and adequate hydration',
        'Over-the-counter pain relief as needed',
        'Monitor blood pressure',
        'Follow-up in 1 week if symptoms persist',
      ],
      status: 'completed',
    };
  }

  static generateMockProfile() {
    return {
      id: 'user-001',
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com',
      dateOfBirth: '1988-05-15',
      gender: 'M',
      phone: '+1-555-123-4567',
      address: {
        street: '123 Main St',
        city: 'New York',
        state: 'NY',
        zip: '10001',
        country: 'USA',
      },
      medicalHistory: [],
      allergies: ['Penicillin'],
      medications: [],
    };
  }
}

/**
 * Mock API Service
 */
class MockApiService {
  private delay: number = 500; // Simulate network delay
  private conversations: Map<string, any> = new Map();
  private reports: Map<string, any> = new Map();

  constructor(delay: number = 500) {
    this.delay = delay;
    this.initializeMockData();
  }

  /**
   * Initialize with sample data
   */
  private initializeMockData(): void {
    for (let i = 0; i < 3; i++) {
      const conv = MockDataGenerator.generateMockConversation();
      this.conversations.set(conv.id, conv);

      const report = MockDataGenerator.generateMockReport(undefined);
      report.conversationId = conv.id;
      this.reports.set(report.id, report);
    }
  }

  /**
   * Simulate delay
   */
  private async simulateDelay(): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, this.delay));
  }

  /**
   * Simulate API call
   */
  async handleRequest(endpoint: string, options: RequestOptions = {}): Promise<any> {
    await this.simulateDelay();

    const method = options.method || 'GET';
    const body = options.body as any;

    // Conversations endpoints
    if (endpoint.match(/^\/conversations$/) && method === 'POST') {
      return { id: MockDataGenerator.generateConversationId(), ...body };
    }

    if (endpoint.match(/^\/conversations\/.+$/) && method === 'GET') {
      const id = endpoint.split('/')[2];
      return this.conversations.get(id) || MockDataGenerator.generateMockConversation(id);
    }

    if (endpoint === '/conversations' && method === 'GET') {
      return {
        conversations: Array.from(this.conversations.values()),
        total: this.conversations.size,
      };
    }

    if (endpoint.match(/^\/conversations\/\d+\/messages$/) && method === 'POST') {
      return {
        id: MockDataGenerator.generateMessageId(),
        role: 'assistant',
        content: 'This is a mock response from the AI assistant.',
        timestamp: new Date().toISOString(),
      };
    }

    if (endpoint.match(/^\/conversations\/.+\/report$/) && method === 'GET') {
      return MockDataGenerator.generateMockReport();
    }

    if (endpoint.match(/^\/conversations\/.+\/export\/pdf$/) && method === 'GET') {
      // Return mock PDF blob
      const content = 'Mock PDF content';
      return new Blob([content], { type: 'application/pdf' });
    }

    // Patient endpoints
    if (endpoint === '/patient/profile' && method === 'GET') {
      return MockDataGenerator.generateMockProfile();
    }

    if (endpoint === '/patient/profile' && method === 'PUT') {
      return { ...MockDataGenerator.generateMockProfile(), ...body };
    }

    if (endpoint === '/patient/medical-history' && method === 'GET') {
      return {
        conditions: ['Hypertension', 'Allergies'],
        surgeries: ['Appendectomy (2010)'],
      };
    }

    // Reports endpoints
    if (endpoint === '/reports' && method === 'GET') {
      return {
        reports: Array.from(this.reports.values()),
        total: this.reports.size,
      };
    }

    if (endpoint.match(/^\/reports\/.+$/) && method === 'GET') {
      const id = endpoint.split('/')[2];
      return this.reports.get(id) || MockDataGenerator.generateMockReport(id);
    }

    // Default response
    return { success: true, message: 'Mock API call completed' };
  }

  /**
   * Clear mock data
   */
  clear(): void {
    this.conversations.clear();
    this.reports.clear();
    this.initializeMockData();
  }

  /**
   * Add mock conversation
   */
  addConversation(conversation: any): void {
    this.conversations.set(conversation.id, conversation);
  }

  /**
   * Add mock report
   */
  addReport(report: any): void {
    this.reports.set(report.id, report);
  }

  /**
   * Get statistics
   */
  getStats(): any {
    return {
      totalConversations: this.conversations.size,
      totalReports: this.reports.size,
      averageResponseTime: this.delay,
    };
  }
}

// Create singleton instance
const mockApiService = new MockApiService();

export default mockApiService;
export { MockApiService, MockDataGenerator };
