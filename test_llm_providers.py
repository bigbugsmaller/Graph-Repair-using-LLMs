#!/usr/bin/env python3
"""
Test script to verify LLM provider configuration.
Tests both Ollama and LM Studio connectivity.
"""

import sys
import config
from graph_repair.llm.client import get_llm_client


def test_provider_connection():
    """Test connection to configured LLM provider"""
    provider = config.LLM_PROVIDER.lower()
    
    print(f"Testing LLM Provider: {provider.upper()}")
    print("=" * 50)
    
    try:
        client = get_llm_client()
        
        if provider == "lm-studio":
            print(f"   Host: {config.LM_STUDIO_HOST}")
            print(f"   Model: {config.LM_STUDIO_MODEL}")
            
            # Test a simple completion
            print("\n🧪 Testing completion...")
            response = client.chat.completions.create(
                model=config.LM_STUDIO_MODEL,
                messages=[{"role": "user", "content": "Say 'Hello, LM Studio!' and nothing else."}],
                max_tokens=20,
                stream=False
            )
            result = response.choices[0].message.content
            print(f"✅ Successfully connected to {provider}")
            print(f"   Response: {result}")
            
        else:  # ollama
            print(f"   Host: {config.OLLAMA_HOST}")
            print(f"   Model: {config.OLLAMA_MODEL}")
            
            # Test a simple completion
            print("\n🧪 Testing completion...")
            response = client.chat(
                config.OLLAMA_MODEL,
                messages=[{"role": "user", "content": "Say 'Hello, Ollama!' and nothing else."}],
                stream=False
            )
            result = response['message']['content']
            print(f"✅ Successfully connected to {provider}")
            print(f"   Response: {result}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        
        if provider == "lm-studio":
            print("1. Ensure LM Studio is running")
            print("2. Check that a model is loaded in the 'Local Server' tab")
            print("3. Verify the server is started (green indicator)")
            print(f"4. Test connection: curl {config.LM_STUDIO_HOST}/v1/models")
        else:
            print("1. Ensure Ollama is running: ollama serve")
            print("2. Check that the model is installed: ollama list")
            print(f"3. Pull the model if needed: ollama pull {config.OLLAMA_MODEL}")
            print(f"4. Test connection: curl {config.OLLAMA_HOST}/api/tags")
            if config.OLLAMA_HOST == config.LM_STUDIO_HOST or config.OLLAMA_HOST.endswith(":1234"):
                print("5. Port 1234 is commonly used by LM Studio, not Ollama. If you mean Ollama, OLLAMA_HOST is usually http://localhost:11434")
        
        return False


def show_config():
    """Display current configuration"""
    print("\n📋 Current Configuration")
    print("=" * 50)
    print(f"LLM_PROVIDER: {config.LLM_PROVIDER}")
    print(f"\nOllama Settings:")
    print(f"  OLLAMA_HOST: {config.OLLAMA_HOST}")
    print(f"  OLLAMA_MODEL: {config.OLLAMA_MODEL}")
    print(f"\nLM Studio Settings:")
    print(f"  LM_STUDIO_HOST: {config.LM_STUDIO_HOST}")
    print(f"  LM_STUDIO_MODEL: {config.LM_STUDIO_MODEL}")
    print("=" * 50)


def main():
    """Main test function"""
    print("\n🔍 LLM Provider Test Suite\n")
    
    show_config()
    print()
    
    success = test_provider_connection()
    
    if success:
        print("\n🎉 Your LLM provider is configured correctly!")
        print("You can now run: python3 main.py")
        sys.exit(0)
    else:
        print("\n⚠️  Please fix the issues above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
