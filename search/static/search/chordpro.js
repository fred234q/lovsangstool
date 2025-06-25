import ChordSheetJS from './bundle.js';

document.addEventListener('DOMContentLoaded', () => {
    const songId = document.querySelector('#lyrics-container').dataset.songId;
    parse_song(songId);
});

// Get new search results via metasearch in Python
// const queryString = window.location.search;
// const urlParams = new URLSearchParams(queryString);
// const query = urlParams.get('q')
// fetch(`/get-songs/${query}`)

function parse_song(songId) {

    fetch(`/sang/${songId}/chordpro`)
    .then(response => response.json())
    .then(chordproObject => {
        // Print song
        console.log(chordproObject)
        const chordproLyrics = chordproObject.chordpro

        const chordSheet = chordproLyrics.substring(1);

        const parser = new ChordSheetJS.ChordProParser();
        const song = parser.parse(chordSheet);

        const formatter = new ChordSheetJS.HtmlDivFormatter();
        const disp = formatter.format(song);

        const lyricsContainer = document.querySelector('#lyrics-container');
        lyricsContainer.innerHTML = disp;

        const paragraphs = lyricsContainer.querySelectorAll('.paragraph');

        // First hide all chords (CSS alternative)
        const style = document.createElement('style');
        style.textContent = '.chord { display: none !important; }';
        document.head.appendChild(style);

        // Process each paragraph
        paragraphs.forEach(paragraph => {
            const rows = paragraph.querySelectorAll('.row');
            let formattedParagraph = document.createElement('div');
            formattedParagraph.className = 'lyrics-paragraph';

            rows.forEach(row => {
                // Handle section headers (like "Vers 1")
                if (row.querySelector('.comment')) {
                    const header = document.createElement('div');
                    header.className = 'section-header';
                    header.textContent = row.querySelector('.comment').textContent;
                    formattedParagraph.appendChild(header);
                    return;
                }

                // Process lyric lines
                const lineDiv = document.createElement('div');
                lineDiv.className = 'lyric-line';
                
                const columns = row.querySelectorAll('.column');
                let lineText = '';
                
                columns.forEach(column => {
                    const lyric = column.querySelector('.lyrics')?.textContent || '';
                    lineText += lyric;
                });

                lineDiv.textContent = lineText.trim();
                if (lineText.trim()) {
                    formattedParagraph.appendChild(lineDiv);
                }
            });

            paragraph.replaceWith(formattedParagraph);
        });

        // Clean up empty paragraphs
        document.querySelectorAll('div').forEach(el => {
            if (!el.textContent.trim() && !el.children.length) {
                el.remove();
            }
        });


    })
    .catch(error => {
        console.log('Error:', error);
    });


}

