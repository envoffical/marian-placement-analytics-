
let scatterChart, radarChart, donutChart;

function initCharts(students) {
    Chart.defaults.color = '#64748b';
    Chart.defaults.font.family = 'Inter';

    // 1. Scatter Chart (CGPA vs Readiness)
    const scatterData = students.map(s => ({x: s.cgpa, y: s.portfolio_readiness, r: 6, name: s.name}));
    
    const ctxScatter = document.getElementById('scatterChart').getContext('2d');
    if(scatterChart) scatterChart.destroy();
    scatterChart = new Chart(ctxScatter, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Students',
                data: scatterData,
                backgroundColor: 'rgba(220, 38, 38, 0.6)',
                borderColor: 'rgba(220, 38, 38, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.raw.name}: CGPA ${ctx.raw.x}, Score ${ctx.raw.y}`
                    }
                }
            },
            onClick: (e, elements) => {
                if (elements.length > 0) {
                    const idx = elements[0].index;
                    const studentName = scatterData[idx].name;
                    const student = window.allStudents.find(s => s.name === studentName);
                    if(student && window.openModal) window.openModal(student);
                } else {
                    alert("Dashboard Purpose: Evaluate placement readiness across technical and behavioral matrices.\n\nFor queries, contact Admin:\nEmail: placement@college.edu\nPhone: +91-9876543210");
                }
            },
            scales: {
                x: { title: {display: true, text: 'CGPA'}, min: 5, max: 10, grid: { color: 'rgba(0,0,0,0.04)' } },
                y: { title: {display: true, text: 'Readiness Score'}, min: 0, max: 100, grid: { color: 'rgba(0,0,0,0.04)' } }
            }
        }
    });

    // 2. Radar Chart (Cohort Average Skills/Domains)
    const domainScores = {};
    students.forEach(s => {
        s.domains.forEach(d => {
            domainScores[d] = (domainScores[d] || 0) + 1;
        });
    });
    
    const topDomains = Object.entries(domainScores).sort((a,b) => b[1] - a[1]).slice(0, 6);
    
    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    if(radarChart) radarChart.destroy();
    radarChart = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: topDomains.map(d => d[0]),
            datasets: [{
                label: 'Domain Interest Volume',
                data: topDomains.map(d => d[1]),
                backgroundColor: 'rgba(225, 29, 72, 0.1)',
                borderColor: 'rgba(225, 29, 72, 0.8)',
                pointBackgroundColor: 'rgba(225, 29, 72, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(0,0,0,0.05)' },
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    pointLabels: { color: '#475569', font: {size: 10} },
                    ticks: { display: false }
                }
            },
            onClick: (e, elements) => {
                alert("Dashboard Purpose: Evaluate placement readiness across technical and behavioral matrices.\n\nFor queries, contact Admin:\nEmail: placement@college.edu\nPhone: +91-9876543210");
            },
            plugins: { legend: { display: false } }
        }
    });

    // 3. Donut Chart (Experience Matrix)
    let withInternship = 0, withCerts = 0, both = 0, neither = 0;
    students.forEach(s => {
        if(s.has_internship && s.has_cert) both++;
        else if(s.has_internship) withInternship++;
        else if(s.has_cert) withCerts++;
        else neither++;
    });

    const ctxDonut = document.getElementById('donutChart').getContext('2d');
    if(donutChart) donutChart.destroy();
    donutChart = new Chart(ctxDonut, {
        type: 'doughnut',
        data: {
            labels: ['Both', 'Internship Only', 'Cert Only', 'Neither'],
            datasets: [{
                data: [both, withInternship, withCerts, neither],
                backgroundColor: [
                    'rgba(153, 27, 27, 0.8)', // Dark Red
                    'rgba(220, 38, 38, 0.8)', // Primary Red
                    'rgba(248, 113, 113, 0.8)', // Light Red
                    'rgba(226, 232, 240, 0.8)'  // Gray
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (e, elements) => {
                alert("Dashboard Purpose: Evaluate placement readiness across technical and behavioral matrices.\n\nFor queries, contact Admin:\nEmail: placement@college.edu\nPhone: +91-9876543210");
            },
            plugins: {
                legend: { position: 'right', labels: { color: '#475569', font: {size: 11} } }
            },
            cutout: '75%'
        }
    });
}
        