import React, { useState, useRef } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { useStartSession, useSendMessage, useFinishSession, Message, Session } from './hooks';
import { theme } from '../../theme';
import { LinearGradient } from 'expo-linear-gradient';
import { Bot, FileText, Send, ChevronLeft } from 'lucide-react-native';

export const InterviewScreen = () => {
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  const startSession = useStartSession();
  const sendMessage = useSendMessage();
  const finishSession = useFinishSession();

  const handleStart = (type: 'SCRIPTED' | 'AI') => {
    startSession.mutate(type, {
      onSuccess: (data) => {
        setSession(data);
        setMessages(data.messages);
      },
      onError: (err: any) => {
        alert(err.response?.data?.error || 'Failed to start session');
      }
    });
  };

  const handleSend = () => {
    if (!inputText.trim() || !session) return;
    
    const userMsgText = inputText.trim();
    setInputText('');

    const optimisticMsg: Message = { id: Date.now(), role: 'USER', text: userMsgText, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, optimisticMsg]);

    sendMessage.mutate(
      { sessionId: session.id, text: userMsgText },
      {
        onSuccess: (botMsg) => {
          setMessages(prev => [...prev, botMsg]);
        },
        onError: () => {
          alert('Failed to send message');
        }
      }
    );
  };

  const handleFinish = () => {
    if (!session) return;
    finishSession.mutate(session.id, {
      onSuccess: (data) => {
        setSession(data);
        alert(`Session Finished! Score: ${data.score}`);
      }
    });
  };

  if (!session) {
    return (
      <View style={styles.setupContainer}>
        <Text style={styles.header}>Choose Mode</Text>
        
        <TouchableOpacity activeOpacity={0.9} onPress={() => handleStart('SCRIPTED')} disabled={startSession.isPending}>
          <LinearGradient
            colors={['#2563EB', '#1D4ED8']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.modeCard}
          >
            <View style={styles.iconCircle}>
              <FileText color="#2563EB" size={24} />
            </View>
            <View style={styles.cardContent}>
              <View style={styles.badgeRow}>
                <View style={styles.difficultyBadge}><Text style={styles.badgeText}>MEDIUM</Text></View>
                <View style={styles.durationBadge}><Text style={styles.badgeText}>10 Qs</Text></View>
              </View>
              <Text style={styles.cardTitle}>Scripted Mode</Text>
              <Text style={styles.cardDesc}>Answer pre-defined architectural questions from the system.</Text>
            </View>
          </LinearGradient>
        </TouchableOpacity>

        <TouchableOpacity activeOpacity={0.9} onPress={() => handleStart('AI')} disabled={startSession.isPending}>
          <LinearGradient
            colors={['#8B5CF6', '#6D28D9']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.modeCard}
          >
            <View style={styles.iconCircle}>
              <Bot color="#8B5CF6" size={24} />
            </View>
            <View style={styles.cardContent}>
              <View style={styles.badgeRow}>
                 <View style={styles.difficultyBadge}><Text style={styles.badgeText}>HARD</Text></View>
                 <View style={styles.durationBadge}><Text style={styles.badgeText}>15 mins</Text></View>
              </View>
              <Text style={styles.cardTitle}>AI Practice Mode</Text>
              <Text style={styles.cardDesc}>Simulated live conversation with HR AI. Adapts dynamically.</Text>
            </View>
          </LinearGradient>
        </TouchableOpacity>

        {startSession.isPending && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
            <Text style={styles.loadingText}>Initializing Environment...</Text>
          </View>
        )}
      </View>
    );
  }

  const renderBubble = ({ item }: { item: Message }) => {
    const isUser = item.role === 'USER';
    return (
      <View style={[styles.bubbleWrapper, isUser ? styles.bubbleUser : styles.bubbleBot]}>
        {!isUser && (
           <View style={styles.botAvatar}>
             <Bot size={16} color={theme.colors.primary.DEFAULT} />
           </View>
        )}
        <View style={[styles.bubble, isUser ? styles.bgUser : styles.bgBot]}>
          <Text style={[styles.bubbleText, isUser && styles.bubbleTextUser]}>{item.text}</Text>
        </View>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView 
      style={styles.chatContainer} 
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.chatHeader}>
        <View style={styles.headerTitleRow}>
          <TouchableOpacity onPress={() => setSession(null)}>
            <ChevronLeft color={theme.colors.text.primary} size={28} />
          </TouchableOpacity>
          <Text style={styles.chatTitle}>{session.type === 'AI' ? 'HR Bot' : 'Scripted Session'}</Text>
        </View>
        {session.status === 'ACTIVE' && (
          <TouchableOpacity onPress={handleFinish} style={styles.endButton}>
            <Text style={styles.finishText}>End Session</Text>
          </TouchableOpacity>
        )}
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderBubble}
        contentContainerStyle={styles.listContent}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {session.status === 'ACTIVE' ? (
        <View style={styles.inputArea}>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type your response..."
            placeholderTextColor={theme.colors.text.muted}
            multiline
          />
          <TouchableOpacity 
            style={[styles.sendButton, !inputText.trim() && { opacity: 0.5 }]} 
            onPress={handleSend}
            disabled={!inputText.trim() || sendMessage.isPending}
          >
            {sendMessage.isPending ? <ActivityIndicator color="#FFF" /> : <Send size={20} color="#FFF" />}
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.scoreArea}>
          <View style={styles.scoreCard}>
            <Text style={styles.scoreLabel}>Final Assessment Score</Text>
            <Text style={styles.scoreValue}>{session.score} / 100</Text>
          </View>
          <TouchableOpacity style={styles.resetButton} onPress={() => setSession(null)}>
            <Text style={styles.resetText}>Finish</Text>
          </TouchableOpacity>
        </View>
      )}
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  setupContainer: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary, 
    padding: 24, 
    paddingTop: 80 
  },
  header: { 
    fontSize: theme.typography.size.h1, 
    fontWeight: theme.typography.weight.bold, 
    color: theme.colors.text.primary, 
    marginBottom: 40 
  },
  modeCard: { 
    borderRadius: 24, 
    padding: 24, 
    marginBottom: 20,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  iconCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: theme.colors.text.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 20,
  },
  cardContent: {
    flex: 1,
  },
  badgeRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 12,
  },
  difficultyBadge: {
    backgroundColor: 'rgba(0,0,0,0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  durationBadge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  badgeText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
  cardTitle: { 
    color: '#FFF', 
    fontSize: theme.typography.size.h3, 
    fontWeight: theme.typography.weight.bold, 
    marginBottom: 6 
  },
  cardDesc: { 
    color: 'rgba(255,255,255,0.8)', 
    fontSize: 13,
    lineHeight: 18,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(13, 15, 26, 0.8)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    color: theme.colors.text.primary,
    marginTop: 16,
    fontWeight: theme.typography.weight.semibold,
  },
  
  // Chat Styles
  chatContainer: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary 
  },
  chatHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    padding: 20, 
    paddingTop: 60, 
    backgroundColor: theme.colors.background.modal,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.subtle,
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  chatTitle: { 
    color: theme.colors.text.primary, 
    fontSize: theme.typography.size.h3, 
    fontWeight: theme.typography.weight.bold 
  },
  endButton: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
  },
  finishText: { 
    color: theme.colors.status.error, 
    fontWeight: theme.typography.weight.bold,
    fontSize: 13,
  },
  listContent: {
    padding: 20,
    paddingBottom: 40,
  },
  bubbleWrapper: { 
    marginBottom: 20, 
    width: '100%', 
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  botAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: `${theme.colors.primary.DEFAULT}20`,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
    borderWidth: 1,
    borderColor: `${theme.colors.primary.DEFAULT}40`,
  },
  bubbleUser: { justifyContent: 'flex-end' },
  bubbleBot: { justifyContent: 'flex-start' },
  bubble: { 
    maxWidth: '75%', 
    padding: 16, 
    borderRadius: 20 
  },
  bgUser: { 
    backgroundColor: theme.colors.primary.DEFAULT, 
    borderBottomRightRadius: 4 
  },
  bgBot: { 
    backgroundColor: theme.colors.background.card, 
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  bubbleText: { 
    color: theme.colors.text.secondary, 
    fontSize: 15, 
    lineHeight: 22 
  },
  bubbleTextUser: {
    color: '#FFF',
  },
  inputArea: { 
    flexDirection: 'row', 
    padding: 16, 
    backgroundColor: theme.colors.background.modal, 
    alignItems: 'center', 
    paddingBottom: 40,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.subtle,
  },
  input: { 
    flex: 1, 
    backgroundColor: theme.colors.background.card, 
    borderRadius: 24, 
    paddingHorizontal: 20,
    paddingTop: 14,
    paddingBottom: 14,
    color: theme.colors.text.primary, 
    minHeight: 48, 
    maxHeight: 120,
    fontSize: 16,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  sendButton: { 
    marginLeft: 12, 
    backgroundColor: theme.colors.primary.DEFAULT, 
    width: 48,
    height: 48, 
    borderRadius: 24, 
    justifyContent: 'center', 
    alignItems: 'center',
  },
  scoreArea: { 
    padding: 24, 
    paddingBottom: 60, 
    backgroundColor: theme.colors.background.primary, 
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.subtle,
  },
  scoreCard: {
    width: '100%',
    backgroundColor: `${theme.colors.status.success}10`,
    padding: 24,
    borderRadius: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: `${theme.colors.status.success}30`,
    marginBottom: 24,
  },
  scoreLabel: {
    color: theme.colors.status.success,
    fontSize: 14,
    textTransform: 'uppercase',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  scoreValue: { 
    color: theme.colors.text.primary, 
    fontSize: 32, 
    fontWeight: theme.typography.weight.bold, 
  },
  resetButton: { 
    backgroundColor: theme.colors.background.card, 
    width: '100%',
    padding: 16, 
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  resetText: { 
    color: theme.colors.text.primary, 
    fontWeight: theme.typography.weight.bold,
    fontSize: 16,
  }
});
