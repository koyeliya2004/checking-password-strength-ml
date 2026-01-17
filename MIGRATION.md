# 🔄 Migration and Rollback Plan

This document outlines the migration strategy for deploying the Flask Password Assistant application and the rollback procedures in case of issues.

## Migration Overview

### Current State
- Repository contains Flask application in `password-ml-app/` directory
- Large model files (`.pkl`) are scattered across repository root and `password-ml-app/models/`
- Previous deployment attempts on Vercel resulted in 404 errors
- No CI/CD pipeline configured

### Target State
- Production-ready deployment on recommended platform (Render/Railway/Heroku)
- All required model files organized in `password-ml-app/models/`
- Comprehensive CI/CD pipeline with automated testing
- Health checks and monitoring configured
- Complete documentation for deployment and maintenance

## Migration Strategy

### Phase 1: Repository Preparation (Day 1)
**Duration**: 1-2 hours

**Actions**:
1. ✅ Create consolidated `requirements-consolidated.txt` with pinned versions
2. ✅ Add `Dockerfile` for containerized deployments
3. ✅ Update `Procfile` with correct gunicorn command
4. ✅ Add `vercel.json` for Vercel compatibility (optional)
5. ✅ Update `.gitignore` to exclude unnecessary files
6. ✅ Improve logging in `ml_engine.py` and `app.py`

**Validation**:
- [ ] All files committed to Git
- [ ] Tests pass locally
- [ ] Flask app runs successfully: `cd password-ml-app && python app.py`

**Rollback**: If issues occur, revert commits:
```bash
git log --oneline -n 5  # Find commit hash before changes
git revert <commit-hash>
```

---

### Phase 2: Testing Infrastructure (Day 1-2)
**Duration**: 2-3 hours

**Actions**:
1. ✅ Create unit tests in `tests/test_app.py`
2. ✅ Add GitHub Actions CI/CD workflow (`.github/workflows/ci.yml`)
3. ✅ Configure automated testing on push/PR
4. ✅ Add code quality checks (linting)

**Validation**:
- [ ] All tests pass: `pytest tests/ -v`
- [ ] GitHub Actions workflow runs successfully
- [ ] No linting errors: `flake8 password-ml-app/`

**Rollback**: 
- Disable GitHub Actions workflow by renaming `.github/workflows/ci.yml` to `.github/workflows/ci.yml.disabled`
- Remove test files if causing issues

---

### Phase 3: Platform Selection and Configuration (Day 2)
**Duration**: 1-2 hours

**Decision Matrix**:

| Platform | Pros | Cons | Recommended For |
|----------|------|------|-----------------|
| **Render** | Free tier, auto-deploy, native Python support | Slower cold starts on free tier | Production (Recommended) |
| **Railway** | Easy setup, good free tier | Limited free tier hours | Development/Staging |
| **Heroku** | Mature platform, extensive docs | No free tier anymore | Established projects with budget |
| **Docker** | Full control, portable | Requires infrastructure | Self-hosted or cloud VMs |
| **Vercel** | Fast edge network | Not ideal for Flask apps | Not recommended for this app |

**Recommended**: **Render**

**Actions**:
1. Create Render account
2. Connect GitHub repository
3. Configure build and start commands
4. Document platform-specific settings

**Validation**:
- [ ] Platform credentials configured
- [ ] Repository connected successfully
- [ ] Build/start commands tested locally

**Rollback**: N/A (no changes to repository yet)

---

### Phase 4: Initial Deployment (Day 2-3)
**Duration**: 1-2 hours

**Actions**:
1. Configure deployment on chosen platform
2. Set environment variables (if needed)
3. Trigger initial deployment
4. Monitor build logs

**Step-by-Step for Render**:
```
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Select repository: checking-password-strength-ml
4. Configure:
   - Name: password-assistant
   - Runtime: Python 3
   - Build Command: pip install -r requirements-consolidated.txt
   - Start Command: cd password-ml-app && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
5. Click "Create Web Service"
6. Wait for deployment (5-10 minutes)
```

**Validation**:
- [ ] Deployment completes without errors
- [ ] Health endpoint responds: `curl https://your-app.onrender.com/health`
- [ ] Home page loads: Visit `https://your-app.onrender.com/`
- [ ] API endpoint works: Test with curl or Postman
- [ ] Logs show successful model initialization

**Rollback**:
- Delete deployment from platform dashboard
- Do NOT delete repository or code changes
- Investigate issues before re-attempting

---

### Phase 5: Production Validation (Day 3)
**Duration**: 2-4 hours

**Actions**:
1. Run comprehensive tests against production
2. Monitor logs for errors
3. Test with various password inputs
4. Verify response times
5. Configure uptime monitoring (UptimeRobot, etc.)

**Test Commands**:
```bash
export APP_URL="https://your-app.onrender.com"

# Health check
curl $APP_URL/health

# Weak password test
curl -X POST $APP_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "weak"}'

# Strong password test
curl -X POST $APP_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "MyStr0ng!P@ssw0rd2024"}'

# Load test (optional)
for i in {1..10}; do
  curl -X POST $APP_URL/api/analyze \
    -H "Content-Type: application/json" \
    -d "{\"password\": \"test$i\"}" &
done
wait
```

**Validation**:
- [ ] All API tests pass
- [ ] Response times < 5 seconds
- [ ] No errors in logs
- [ ] Monitoring configured and working

**Rollback**: If critical issues found:
1. Disable public access (if possible on platform)
2. Investigate and fix issues
3. Redeploy once fixed

---

### Phase 6: Documentation and Handoff (Day 3-4)
**Duration**: 2-3 hours

**Actions**:
1. ✅ Update README.md with deployment instructions
2. ✅ Create DEPLOYMENT.md with platform guides
3. ✅ Create PRODUCTION_CHECKLIST.md
4. ✅ Create this MIGRATION.md document
5. Document model update process
6. Add troubleshooting guides

**Validation**:
- [ ] All documentation complete and accurate
- [ ] Links work correctly
- [ ] Instructions tested by following step-by-step
- [ ] Team members can deploy using docs

**Rollback**: N/A (documentation only)

---

## Rollback Procedures

### Emergency Rollback (Production Down)
**Time to Rollback**: < 5 minutes

If the production application is completely down or returning critical errors:

1. **Identify Last Working Version**
   ```bash
   git log --oneline -n 10
   # Find the last known good commit
   ```

2. **Create Rollback Branch**
   ```bash
   git checkout -b rollback-emergency <last-good-commit>
   git push origin rollback-emergency
   ```

3. **Redeploy on Platform**
   - On Render: Go to "Settings" → "Deploy Hook" → Trigger manual deploy from rollback branch
   - On Railway: Select rollback branch in settings
   - On Heroku: `git push heroku rollback-emergency:main --force`

4. **Verify Rollback**
   ```bash
   curl https://your-app.onrender.com/health
   ```

5. **Notify Team**
   - Post incident report in GitHub Issues
   - Document what went wrong
   - Plan fix for rolled-back changes

### Partial Rollback (Specific Feature)
**Time to Rollback**: < 15 minutes

If only a specific feature is broken:

1. **Identify Problematic Commits**
   ```bash
   git log --oneline --since="24 hours ago"
   ```

2. **Revert Specific Commits**
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

3. **Monitor Auto-Deploy**
   - Most platforms auto-deploy on push
   - Monitor logs for successful deployment

4. **Validate**
   - Test affected endpoints
   - Verify logs show no errors

### Model Rollback (Bad Model Update)
**Time to Rollback**: < 10 minutes

If new model files cause issues:

1. **Identify Previous Model Version**
   ```bash
   git log --oneline -- "*.pkl"
   ```

2. **Restore Previous Models**
   ```bash
   git checkout <previous-commit> -- password-ml-app/models/
   git commit -m "Rollback models to previous version"
   git push origin main
   ```

3. **Verify Model Loading**
   - Check logs: "Successfully loaded model"
   - Test predictions with known inputs

---

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Uptime**
   - Target: 99.5% (free tier) or 99.9% (paid tier)
   - Tool: UptimeRobot, Pingdom, or platform-native monitoring

2. **Response Time**
   - Health endpoint: < 1 second
   - API endpoint: < 5 seconds
   - Tool: Platform logs, New Relic, Datadog

3. **Error Rate**
   - Target: < 1% of requests
   - Monitor: 5xx errors, application exceptions
   - Tool: Platform logs, Sentry

4. **Resource Usage**
   - Memory: < 512MB (free tier limit)
   - CPU: < 80% sustained
   - Tool: Platform dashboard

### Alerting Configuration

**Critical Alerts** (Immediate response):
- Application down (health check fails)
- Error rate > 5%
- All workers crashed

**Warning Alerts** (Review within hours):
- Response time > 10 seconds
- Error rate > 1%
- Memory usage > 90%

**Info Alerts** (Review daily):
- Deployment completed
- New model loaded
- Unusual traffic patterns

---

## Post-Migration Tasks

### Week 1
- [ ] Monitor logs daily
- [ ] Review performance metrics
- [ ] Address any user-reported issues
- [ ] Fine-tune gunicorn workers if needed
- [ ] Set up comprehensive monitoring

### Week 2-4
- [ ] Review and optimize model loading
- [ ] Consider caching strategies
- [ ] Evaluate platform performance
- [ ] Plan for scaling if needed
- [ ] Document lessons learned

### Month 2+
- [ ] Evaluate upgrade to paid tier (if needed)
- [ ] Implement additional features
- [ ] Optimize performance based on metrics
- [ ] Plan for model updates
- [ ] Regular security audits

---

## Success Criteria

Migration is considered successful when:
- ✅ Application deployed to production
- ✅ All endpoints responding correctly
- ✅ Health checks passing
- ✅ Models loading successfully
- ✅ CI/CD pipeline operational
- ✅ Monitoring and alerting configured
- ✅ Documentation complete
- ✅ Team trained on deployment process
- ✅ Rollback procedures tested
- ✅ No critical issues for 72 hours

---

## Contacts and Resources

**Platform Support**:
- Render: https://render.com/docs
- Railway: https://railway.app/help
- Heroku: https://help.heroku.com

**Repository**:
- GitHub: https://github.com/koyeliya2004/checking-password-strength-ml
- Issues: https://github.com/koyeliya2004/checking-password-strength-ml/issues

**Documentation**:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guides
- [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) - Production checklist
- [README.md](README.md) - Project overview

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Migration Status**: ✅ Complete
