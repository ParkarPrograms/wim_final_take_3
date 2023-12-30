function generatePDF() {
    const element = document.getElementById("invoice");
  
    html2pdf()
      .from(element)
      .outputPdf()
      .then((pdf) => {
        // Add more elements or charts if needed
        pdf.addPage().html(document.getElementById("curve_chart"));
        pdf.addPage().html(document.getElementById("piechart_3d"));
        pdf.addPage().html(document.getElementById("demographics_pie_chart"));
        
        // Save the complete PDF
        pdf.save();
      });
  }