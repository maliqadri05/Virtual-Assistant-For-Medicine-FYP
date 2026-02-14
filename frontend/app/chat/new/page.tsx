'use client';

import { ConversationContainer } from '@/components/ConversationView';
import { ProtectedRoute } from '@/components/ProtectedRoute';

function ChatContent() {
  return <ConversationContainer showSidebar={true} />;
}

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatContent />
    </ProtectedRoute>
  );
}
