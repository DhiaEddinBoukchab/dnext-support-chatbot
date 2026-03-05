import { Metadata } from 'next'
import ChatLayout from '@/components/chat-layout'

export const metadata: Metadata = {
  title: 'Chat - DNEXT Support',
}

export default function Home() {
  return <ChatLayout />
}
