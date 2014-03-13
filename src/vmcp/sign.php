<?php

/**
 * Sign the data in the given dictionary and return a new hash
 * that includes the signature. 
 *
 * @param $data Is a dictionary that contains the values to be signed
 * @param $salt Is the salt parameter passed via the cvm_salt GET parameter
 * @param $pkey Is the path to the private key file that will be used to calculate the signature
 */
function sign_data( $data, $salt, $pkey ) {

    // Sort keys
    ksort( $data );

    // Calculate buffer to sign
    $buffer = "";
    foreach ($data as $k => $v) {
        
        // The boolean is a special case and should also be
        // updated to the data array
        if (is_bool($v)) {
           $v = $data[$k] = ( $v ? "1" : "0" );
        }
        
        // Update buffer
        $buffer .= strtolower($k) . "=" . rawurlencode( $v ) . "\n";
    }

    // Append salt
    $buffer.=$salt;

    // Sign data using OpenSSL_Sign
    openssl_sign( $buffer, $signature, "file://$pkey", "sha512" );
    $data['signature'] = base64_encode($signature);

    // Return hash
    return $data;
    
}

$data = array(
    'name' => $_GET['name'],
    'secret' => 'secret',
    'userData' => "[amiconfig]\nplugins=cernvm\n[cernvm]\ncontextualization_key=" . $_GET['contextualization_key']. "\n",
    'ram' => $_GET['ram'],
    'cpus' => $_GET['cpus'],
    'disk' => $_GET['disk'],
    'version' => $_GET['ucernvm_version'],
    // 64bit, headful, full GUI support
    'flags' => 0x01 | 0x10 | 0x20,
);

echo json_encode( sign_data( $data, $_GET['cvm_salt'], "/usr/local/cernvm-private/private.pem" ) );

?>
