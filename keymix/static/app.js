$(document).ready(function () {

	// Check for click events on the navbar burger icon
	$(".navbar-burger").click(function () {

		// Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
		$(".navbar-burger").toggleClass("is-active");
		$(".navbar-menu").toggleClass("is-active");

	});
});

const $subsearch = $("#subsearch");
const $subsearch_results = $("#subsearch_results");
const $subsearch_button = $("#subsearch_button");

$subsearch_button.on("click", async function (evt) {
	evt.preventDefault();
	$subsearch_results.empty()

	const seed_id = await getId(
		$("#subsearch_input").val(),
		$("input[name='subsearch_radio']:checked").val()
	);
	console.log(seed_id);

	if (seed_id.data.artists) {
		for (result of seed_id.data.artists.items) {
			artist = `
            <label class="checkbox">
              <input type="checkbox" name="artist" value="${result.id}">
              ${result.name}
            </label>`;
			$subsearch_results.append(artist);
		}
	}

	if (seed_id.data.tracks) {
		for (result of seed_id.data.tracks.items) {
			track = `
            <label class="checkbox">
              <input type="checkbox" name="track" value="${result.id}">
              ${result.name}
            </label>`;
			// $subsearch_results.clear()
			$subsearch_results.append(track);
		}
	}
});

async function getId(inputName, inputType) {
	resp = await axios.get("/subsearch", {
		params: { q: inputName, type: inputType },
	});
	return resp;
}
