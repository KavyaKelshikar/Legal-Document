import sys
import os
import asyncio
import httpx

sys.path.insert(0, os.path.abspath('backend'))
from src.main import app

async def run_tests():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test login page at /
        res_login = await client.get('/')
        assert res_login.status_code == 200, f'Login page failed: {res_login.status_code}'
        assert 'Sign In' in res_login.text or 'login' in res_login.text.lower()
        print('1. Login page (/) test passed!')

        # 2. Test main application at /app
        res_app = await client.get('/app')
        assert res_app.status_code == 200, f'App failed: {res_app.status_code}'
        assert 'LexiCore' in res_app.text
        assert 'view-dashboard' in res_app.text
        assert 'view-analysis' in res_app.text
        assert 'view-documents' in res_app.text
        assert 'view-search' in res_app.text
        assert 'view-ai-assistant' in res_app.text
        print('2. Main dashboard (/app) test passed!')

        # 3. Test app.js
        res_js = await client.get('/static/app.js')
        assert res_js.status_code == 200
        assert 'LexiCore' in res_js.text
        print('3. Static app.js test passed!')

        # 4. Test uploading a sample pdf to /api/v1/analyze
        pdf_path = 'backend/sample_pdfs/High_Risk_Vendor_Contract.pdf'
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        upload_res = await client.post(
            '/api/v1/analyze',
            files={'file': ('High_Risk_Vendor_Contract.pdf', pdf_bytes, 'application/pdf')}
        )
        assert upload_res.status_code == 200, f'Upload failed: {upload_res.text}'
        doc = upload_res.json()
        doc_id = doc['document_id']
        overall_risk = doc.get('document_risk', {}).get('overall_level', 'LOW')
        overall_score = doc.get('document_risk', {}).get('overall_score', 0)
        print(f"4. Upload API passed! Doc ID: {doc_id}, Risk: {overall_risk}, Score: {overall_score}")

        # 5. Test documents vault list
        docs_res = await client.get('/api/v1/documents')
        assert docs_res.status_code == 200
        docs = docs_res.json()
        assert len(docs) >= 1
        print(f'5. Documents vault API passed! Total docs in vault: {len(docs)}')

        # 6. Test summary
        sum_res = await client.get(f'/api/v1/documents/{doc_id}/summary')
        assert sum_res.status_code == 200
        print('6. Extractive summary API passed!', list(sum_res.json().keys()))

        # 7. Test missing clauses
        miss_res = await client.get(f'/api/v1/documents/{doc_id}/missing-clauses')
        assert miss_res.status_code == 200
        print('7. Missing clauses API passed! Missing:', [c['category'] for c in miss_res.json().get('missing_clauses', [])])

        # 8. Test search (GET)
        search_res = await client.get(f'/api/v1/documents/{doc_id}/search?question=payment terms')
        assert search_res.status_code == 200
        s_data = search_res.json()
        print(f"8. TF-IDF Search API passed! Found: {s_data.get('found')}, Answer: {s_data.get('answer')[:50]}...")

        # 9. Test report download
        rep_res = await client.get(f'/api/v1/documents/{doc_id}/report')
        assert rep_res.status_code == 200
        assert rep_res.headers['content-type'] == 'application/pdf'
        print(f'9. PDF report download API passed! Size: {len(rep_res.content)} bytes')

        # 10. Test overall analytics
        analytics_res = await client.get('/api/v1/analytics')
        assert analytics_res.status_code == 200
        an_data = analytics_res.json()
        print(f"10. Dashboard analytics API passed! Total docs: {an_data['total_documents']}, Avg score: {an_data['average_risk_score']}")

        print('\n======================================================')
        print('ALL 10 FRONTEND & BACKEND INTEGRATION TESTS PASSED!')
        print('======================================================')

if __name__ == '__main__':
    asyncio.run(run_tests())
