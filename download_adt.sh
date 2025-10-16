# aria_dataset_download -c ./ADT_download_urls.json -o ./temp -l all -d 6
# aria_dataset_downloader -c ./ADT_download_urls.json -o ./temp -l Apartment_release_clean_seq131_M1292 -d 0 1 2 3 4 5 6 7 8 9 
# aria_dataset_downloader -c ./ADT_download_urls.json -o ./temp -l Apartment_release_clean_seq133_M1292 -d 0 1 2 3 6 8 

NAMES=(
    "Apartment_release_meal_skeleton_seq135_M1292"
    "Apartment_release_decoration_seq138_M1292"
    "Apartment_release_golden_skeleton_seq100_M1292"
    "Apartment_release_work_skeleton_seq109_M1292"
)

for NAME in ${NAMES[@]}; do
    echo "Downloading $NAME"
    aria_dataset_downloader -c ./ADT_download_urls.json -o ./temp -l $NAME -d 0 1 2 3 6 8 
done
