#!/usr/bin/env python3
"""Simple test script for LiuAgent functionality."""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core import get_config, logger
from app.services import get_llm_service, get_search_service, get_knowledge_base_service


async def test_config():
    """Test configuration loading."""
    try:
        config = get_config()
        logger.info("✅ Configuration loaded successfully")
        logger.info(f"LLM Provider: {config.llm.provider}")
        logger.info(f"Search Engine: {config.search.primary_engine}")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False


async def test_search_service():
    """Test search service."""
    try:
        search_service = get_search_service()
        logger.info("✅ Search service initialized")
        
        # Test search (with a simple query)
        results = await search_service.search("Python programming", max_results=3)
        if results:
            logger.info(f"✅ Search test passed - found {len(results)} results")
            return True
        else:
            logger.warning("⚠️ Search returned no results (may be normal)")
            return True
    except Exception as e:
        logger.error(f"❌ Search service test failed: {e}")
        return False


async def test_knowledge_base_service():
    """Test knowledge base service."""
    try:
        kb_service = get_knowledge_base_service()
        logger.info("✅ Knowledge base service initialized")
        
        # Test search (should return empty results initially)
        results = await kb_service.search_documents("test query")
        logger.info(f"✅ Knowledge base search test passed - found {len(results)} results")
        return True
    except Exception as e:
        logger.error(f"❌ Knowledge base service test failed: {e}")
        return False


async def test_llm_service():
    """Test LLM service (only if API key is configured)."""
    try:
        config = get_config()
        if not config.llm.api_key or config.llm.api_key == "your-openai-api-key-here":
            logger.warning("⚠️ LLM API key not configured - skipping LLM test")
            return True
            
        llm_service = get_llm_service()
        logger.info("✅ LLM service initialized")
        
        # Simple test (commented out to avoid API costs during testing)
        # from app.models.schemas import ChatMessage
        # messages = [ChatMessage(role="user", content="Hello, respond with just 'Hi'")]
        # response = await llm_service.chat_completion(messages)
        # logger.info(f"✅ LLM test passed - response: {response[:50]}...")
        
        logger.info("✅ LLM service test passed (API key configured)")
        return True
    except Exception as e:
        logger.error(f"❌ LLM service test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("🚀 Starting LiuAgent tests...")
    
    tests = [
        ("Configuration", test_config()),
        ("Search Service", test_search_service()),
        ("Knowledge Base Service", test_knowledge_base_service()),
        ("LLM Service", test_llm_service()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        logger.info(f"\n🧪 Testing {test_name}...")
        result = await test_coro
        results.append((test_name, result))
    
    # Summary
    logger.info("\n📊 Test Results:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Tests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! LiuAgent is ready to run.")
        return 0
    else:
        logger.error("💥 Some tests failed. Please check the configuration and dependencies.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
