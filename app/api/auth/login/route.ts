import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { email, name } = await request.json()

    if (!email || !name) {
      return NextResponse.json(
        { error: 'Missing email or name' },
        { status: 400 }
      )
    }

    // TODO: Call your Python backend auth endpoint
    // Example: const response = await fetch('http://localhost:8000/api/auth/login', {...})

    // For now, return success
    return NextResponse.json(
      {
        success: true,
        user: { email, name },
        message: 'Authentication successful (demo mode)',
      },
      { status: 200 }
    )
  } catch (error) {
    console.error('Auth error:', error)
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 500 }
    )
  }
}
