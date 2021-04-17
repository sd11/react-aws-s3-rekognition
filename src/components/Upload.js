import React, { useRef, useState } from "react";
import S3 from "react-aws-s3";

function Upload() {
  const fileInput = useRef();
  const [data,setData]=useState({});
  const handleClick = (event) => {
    event.preventDefault();
    let file = fileInput.current.files[0];
    let newFileName = fileInput.current.files[0].name.replace(/\..+$/, "");
    const config = {
      bucketName: 'groupneuralnetworkimagebucket1',
      dirName: process.env.REACT_APP_DIR_NAME /* optional */,
      region: 'ap-southeast-2',
      accessKeyId: 'AKIATSAQD7HZPBKIMX7Z',
      secretAccessKey: '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',
    };
    const ReactS3Client = new S3(config);
    ReactS3Client.uploadFile(file, newFileName).then((data) => {
      console.log(data);
      if (data.status === 204) {
        console.log("success");
        fetch('https://groupneuralnetworkrecipebucket1.s3-ap-southeast-2.amazonaws.com/recipes.json'
        ,{
          headers : {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        }
        ).then(function(response){
          console.log(response)
          return response.json();
        }).then(function(myJson) {
          console.log(myJson);
          setData(myJson)
        });
      } else {
        console.log("fail");
      }
    });
  };
  return (
    <div>
      <form className='upload-steps' onSubmit={handleClick}>
        <label>
          Upload file:
          <input type='file' ref={fileInput} />
        </label>
        <br />
        <button type='submit'>Upload</button>
      </form>

      { data && data.recipes && data.recipes.length && (<div>
      <h1>Recipes: </h1>
      <div className="Recipes">
          <p>Ingredients: {data.ingredients}</p>
          { data.recipes.map((recipe) => (
              <div>
                  <p>Recipe Title: {recipe.title}</p>
                  <img src={recipe.image} />
              </div>
          ))}
      </div>
      </div>)}
    </div>
  );
}

export default Upload;
