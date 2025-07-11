// import ChordSheetJS from './bundle.js';
import ChordSheetJS from "https://esm.sh/chordsheetjs";

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

        const paragraphs = document.querySelectorAll('.paragraph');

        console.log(paragraphs);

    })
    .catch(error => {
        console.log('Error:', error);
    });


}

