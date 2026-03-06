import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { conversationId, message } = await request.json()

    if (!conversationId || !message) {
      return NextResponse.json(
        { error: 'Missing conversationId or message' },
        { status: 400 }
      )
    }

    // TODO: Call your Python backend chat endpoint
    // Example: const response = await fetch('http://localhost:8000/api/chat/send', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ conversationId, message })
    // })

    // For demo, return a sample response
    const response = `This is a demo response to: "${message}". Connect your Python backend in app/api/chat/send/route.ts to get real responses.`

    return NextResponse.json(
      {
        success: true,
        conversationId,
        response,
      },
      { status: 200 }
    )
  } catch (error) {
    console.error('Chat error:', error)
    return NextResponse.json(
      { error: 'Failed to send message' },
      { status: 500 }
    )
  }
}
