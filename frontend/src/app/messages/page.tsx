'use client';

import { useState } from 'react';
import { MessageSquare, Send, Search, Circle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface Conversation {
  id: string;
  participantName: string;
  participantAvatar?: string;
  lastMessage: string;
  lastMessageTime: string;
  unreadCount: number;
  isOnline: boolean;
}

interface Message {
  id: string;
  senderId: string;
  text: string;
  timestamp: string;
  isMine: boolean;
}

const mockConversations: Conversation[] = [
  { id: '1', participantName: 'Alex Chen', lastMessage: 'Hey, loved your latest edit!', lastMessageTime: '2m ago', unreadCount: 2, isOnline: true },
  { id: '2', participantName: 'Sarah Kim', lastMessage: 'Can we collab on a project?', lastMessageTime: '15m ago', unreadCount: 0, isOnline: true },
  { id: '3', participantName: 'Marcus Johnson', lastMessage: 'Thanks for the tip!', lastMessageTime: '1h ago', unreadCount: 1, isOnline: false },
  { id: '4', participantName: 'Priya Patel', lastMessage: 'Sure, I\'ll send the files over.', lastMessageTime: '3h ago', unreadCount: 0, isOnline: false },
  { id: '5', participantName: 'Jordan Lee', lastMessage: 'That transition effect was amazing', lastMessageTime: '1d ago', unreadCount: 0, isOnline: false },
];

const mockMessages: Record<string, Message[]> = {
  '1': [
    { id: 'm1', senderId: 'other', text: 'Hey! I saw your latest video.', timestamp: '10:30 AM', isMine: false },
    { id: 'm2', senderId: 'me', text: 'Thanks! Took me a while to get the color grading right.', timestamp: '10:32 AM', isMine: true },
    { id: 'm3', senderId: 'other', text: 'The color grading was on point. What LUT did you use?', timestamp: '10:33 AM', isMine: false },
    { id: 'm4', senderId: 'me', text: 'I actually made a custom one. I can share it with you!', timestamp: '10:35 AM', isMine: true },
    { id: 'm5', senderId: 'other', text: 'Hey, loved your latest edit!', timestamp: '10:40 AM', isMine: false },
  ],
  '2': [
    { id: 'm1', senderId: 'other', text: 'Hi! I have an idea for a collaboration.', timestamp: '9:00 AM', isMine: false },
    { id: 'm2', senderId: 'me', text: 'I\'m listening! What do you have in mind?', timestamp: '9:05 AM', isMine: true },
    { id: 'm3', senderId: 'other', text: 'Can we collab on a project?', timestamp: '9:10 AM', isMine: false },
  ],
};

export default function MessagesPage() {
  const [conversations] = useState<Conversation[]>(mockConversations);
  const [selectedConversation, setSelectedConversation] = useState<string | null>('1');
  const [messageInput, setMessageInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [messages, setMessages] = useState<Record<string, Message[]>>(mockMessages);

  const filteredConversations = conversations.filter(c =>
    c.participantName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const currentMessages = selectedConversation ? (messages[selectedConversation] || []) : [];
  const currentConversation = conversations.find(c => c.id === selectedConversation);

  const handleSendMessage = () => {
    if (!messageInput.trim() || !selectedConversation) return;

    const newMessage: Message = {
      id: `m${Date.now()}`,
      senderId: 'me',
      text: messageInput.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isMine: true,
    };

    setMessages(prev => ({
      ...prev,
      [selectedConversation]: [...(prev[selectedConversation] || []), newMessage],
    }));
    setMessageInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <MessageSquare className="text-blue-500" />
        Messages
      </h1>

      <Card className="overflow-hidden">
        <div className="flex h-[600px]">
          {/* Left Sidebar: Conversation List */}
          <div className="w-80 border-r border-zinc-200 dark:border-zinc-700 flex flex-col">
            {/* Search */}
            <div className="p-3 border-b border-zinc-200 dark:border-zinc-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search conversations..."
                  className="w-full pl-10 pr-4 py-2 text-sm border rounded-lg dark:bg-zinc-800 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Conversation List */}
            <div className="flex-1 overflow-y-auto">
              {filteredConversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => setSelectedConversation(conversation.id)}
                  className={`w-full flex items-start gap-3 p-3 text-left hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors ${
                    selectedConversation === conversation.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                  }`}
                >
                  {/* Avatar */}
                  <div className="relative flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center text-white font-medium text-sm">
                      {conversation.participantName.charAt(0)}
                    </div>
                    {conversation.isOnline && (
                      <Circle size={10} className="absolute bottom-0 right-0 text-green-500 fill-green-500" />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm truncate">{conversation.participantName}</span>
                      <span className="text-[10px] text-zinc-400 flex-shrink-0">{conversation.lastMessageTime}</span>
                    </div>
                    <p className="text-xs text-zinc-500 truncate mt-0.5">{conversation.lastMessage}</p>
                  </div>

                  {conversation.unreadCount > 0 && (
                    <span className="flex-shrink-0 w-5 h-5 bg-blue-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                      {conversation.unreadCount}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Right Panel: Message Thread */}
          <div className="flex-1 flex flex-col">
            {selectedConversation && currentConversation ? (
              <>
                {/* Thread Header */}
                <div className="flex items-center gap-3 p-4 border-b border-zinc-200 dark:border-zinc-700">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center text-white font-medium text-sm">
                    {currentConversation.participantName.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-medium text-sm">{currentConversation.participantName}</h3>
                    <span className={`text-xs ${currentConversation.isOnline ? 'text-green-500' : 'text-zinc-400'}`}>
                      {currentConversation.isOnline ? 'Online' : 'Offline'}
                    </span>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {currentMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.isMine ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[70%] px-3 py-2 rounded-2xl text-sm ${
                          message.isMine
                            ? 'bg-blue-500 text-white rounded-br-md'
                            : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 rounded-bl-md'
                        }`}
                      >
                        <p>{message.text}</p>
                        <span className={`text-[10px] mt-1 block ${message.isMine ? 'text-blue-100' : 'text-zinc-400'}`}>
                          {message.timestamp}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Message Input */}
                <div className="p-4 border-t border-zinc-200 dark:border-zinc-700">
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Type a message..."
                      className="flex-1 px-4 py-2 text-sm border rounded-full dark:bg-zinc-800 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Button
                      size="icon"
                      className="rounded-full"
                      onClick={handleSendMessage}
                      disabled={!messageInput.trim()}
                    >
                      <Send size={16} />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-zinc-400">
                <div className="text-center">
                  <MessageSquare size={48} className="mx-auto mb-2 opacity-50" />
                  <p>Select a conversation to start messaging</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
