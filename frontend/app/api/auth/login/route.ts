import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { email, name } = await request.json()

    // Validate input
    if (!email || !name) {
      return NextResponse.json(
        { error: 'Email and name are required' },
        { status: 400 }
      )
    }

    // Call Python backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name }),
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()

    // Return user data
    return NextResponse.json(
      {
        user: {
          id: data.user_id,
          email: data.email,
          name: data.name,
        },
      },
      { status: 200 }
    )
  } catch (error) {
    console.error('Auth login error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
