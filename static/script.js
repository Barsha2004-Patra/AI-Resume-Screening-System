document.getElementById('screenerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const resultsSection = document.getElementById('resultsSection');
    const analyticsSection = document.getElementById('analyticsSection');
    const resultsBody = document.getElementById('resultsBody');
    const gapInsightsBody = document.getElementById('gapInsightsBody');
    
    submitBtn.disabled = true;
    submitBtn.innerText = 'Analyzing Data Infrastructure Stack...';
    
    const formData = new FormData();
    formData.append('job_title', document.getElementById('job_title').value);
    formData.append('job_description', document.getElementById('job_description').value);
    
    const resumeFiles = document.getElementById('resumes').files;
    for (let i = 0; i < resumeFiles.length; i++) {
        formData.append('resumes', resumeFiles[i]);
    }
    
    try {
        const response = await fetch('/api/screen', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Internal evaluation endpoint pipeline error.');
        }
        
        const data = await response.json();
        resultsBody.innerHTML = '';
        gapInsightsBody.innerHTML = '';
        
        // Render regular table data row by row
        data.results.forEach((item, index) => {
            let scoreClass = 'score-low';
            if (item.match_score >= 75) scoreClass = 'score-high';
            else if (item.match_score >= 45) scoreClass = 'score-medium';
            
            const matchedPills = item.matched_skills.length > 0 
                ? item.matched_skills.map(s => `<span class="pill">${s}</span>`).join('')
                : '<span class="text-muted">None</span>';
                
            const missingPills = item.missing_skills.length > 0 
                ? item.missing_skills.map(s => `<span class="pill pill-missing">${s}</span>`).join('')
                : '<span class="text-muted">None</span>';
                
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${index + 1}</strong></td>
                <td>${item.candidate_name || 'Unknown Candidate'}</td>
                <td>${item.filename}</td>
                <td><span class="score-badge ${scoreClass}">${item.match_score}%</span></td>
                <td>${matchedPills}</td>
                <td>${missingPills}</td>
                <td><a class="action-link" href="/api/report/${item.result_id}" target="_blank">Download Report</a></td>
            `;
            resultsBody.appendChild(tr);

            // Populate actionable steps to fill structural skill gaps
            if (item.missing_skills.length > 0) {
                const insightBlock = document.createElement('div');
                insightBlock.className = 'insight-candidate-block';
                insightBlock.innerHTML = `
                    <h4>Candidate: ${item.candidate_name || 'Unknown'}</h4>
                    <p>To completely bridge the match gap for this position, the candidate must master: <strong>${item.missing_skills.join(', ')}</strong>.</p>
                    <div class="action-pathway"><span>Action Pathway:</span> Prioritize technical assessment questions or structured upskilling around these specific tools.</div>
                `;
                gapInsightsBody.appendChild(insightBlock);
            } else {
                const insightBlock = document.createElement('div');
                insightBlock.className = 'insight-candidate-block target-met';
                insightBlock.innerHTML = `
                    <h4>Candidate: ${item.candidate_name || 'Unknown'}</h4>
                    <p class="text-success">🎉 Matches all technical keywords listed in the job specification metrics.</p>
                `;
                gapInsightsBody.appendChild(insightBlock);
            }
        });
        
        // Initialize visualization graphics rendering engine
        renderMatrixChart(data.results);
        
        analyticsSection.classList.remove('hidden');
        resultsSection.classList.remove('hidden');
        
    } catch (error) {
        alert('Pipeline Interruption Error: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Execute Screening Evaluation';
    }
});

// Canvas rendering routine to draw interactive bar metrics
function renderMatrixChart(candidates) {
    const canvas = document.getElementById('matrixChart');
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const chartData = candidates.slice(0, 5); // Display top 5 entries
    const startX = 60;
    const startY = 30;
    const barMaxHeight = 200;
    const spacing = 40;
    const barWidth = Math.min(50, (canvas.width - startX - (chartData.length * spacing)) / chartData.length);
    
    // Draw background threshold indicator lines
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = startY + (barMaxHeight * (i / 4));
        ctx.beginPath();
        ctx.moveTo(startX, y);
        ctx.lineTo(canvas.width - 20, y);
        ctx.stroke();
        
        ctx.fillStyle = '#64748b';
        ctx.font = '10px sans-serif';
        ctx.fillText(`${100 - (i * 25)}%`, startX - 35, y + 4);
    }
    
    // Process candidate bars individually
    chartData.forEach((c, index) => {
        const currentX = startX + (index * (barWidth + spacing)) + 10;
        const scorePercentage = c.match_score / 100;
        const currentBarHeight = barMaxHeight * scorePercentage;
        const currentY = startY + (barMaxHeight - currentBarHeight);
        
        // Define clean visual fills matching performance rules
        if (c.match_score >= 75) ctx.fillStyle = '#16a34a';
        else if (c.match_score >= 45) ctx.fillStyle = '#ca8a04';
        else ctx.fillStyle = '#dc2626';
        
        // Execute draw
        ctx.fillRect(currentX, currentY, barWidth, currentBarHeight);
        
        // Print values overhead
        ctx.fillStyle = '#0f172a';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${Math.round(c.match_score)}%`, currentX + (barWidth / 2), currentY - 6);
        
        // Label corresponding data names
        ctx.fillStyle = '#334155';
        ctx.font = '11px sans-serif';
        let printableName = c.candidate_name || 'Candidate';
        if (printableName.length > 10) printableName = printableName.substring(0, 8) + '..';
        ctx.fillText(printableName, currentX + (barWidth / 2), startY + barMaxHeight + 18);
    });
}