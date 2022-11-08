VAGRANTFILE_API_VERSION = "2"

# set docker as the default provider
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'

# disable parallellism so that the containers come up in order
ENV['VAGRANT_NO_PARALLEL'] = "1"
ENV['FORWARD_DOCKER_PORTS'] = "1"
# minor hack enabling to run the image and configuration trigger just once
ENV['VAGRANT_EXPERIMENTAL']="typed_triggers"

unless Vagrant.has_plugin?("vagrant-docker-compose")
  system("vagrant plugin install vagrant-docker-compose")
  puts "Dependencies installed, please try the command again."
  exit
end

# Names of Docker images built:
BACKEND_IMAGE  = "dshw/01/client:0.1"

# Node definitions

CLIENTS  = { :nameprefix => "01client-",  # backend nodes get names: backend-1, backend-2, etc.
              :subnet => "10.0.1.",
              :ip_offset => 100,  # backend nodes get IP addresses: 10.0.1.101, .102, .103, etc
              :image => BACKEND_IMAGE }

# Number of CLIENTS to start:
CLIENTS_COUNT = 5

puts "Config section!"

# Common configuration
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.trigger.before :up, type: :command do |trigger|
        trigger.name = "Build docker images"
        trigger.ruby do |env, machine|
            puts "Building node image:"
            `docker build client -t "#{BACKEND_IMAGE}"`
        end
    end
#     config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".*/"
    config.ssh.insert_key = false

    # Definition of N backends
    (1..CLIENTS_COUNT).each do |i|
        node_ip_addr = "#{CLIENTS[:subnet]}#{CLIENTS[:ip_offset] + i}"
        node_name = "#{CLIENTS[:nameprefix]}#{i}"
        node_host_port = 5000 + i
        # Definition of BACKEND
        config.vm.define node_name do |s|
            s.vm.network "private_network", ip: node_ip_addr
            s.vm.network "forwarded_port", guest: 80, host: node_host_port, host_ip: "0.0.0.0", auto_correct: true
            s.vm.hostname = node_name
            s.vm.provider "docker" do |d|
                d.image = CLIENTS[:image]
                d.name = node_name
                d.has_ssh = true
            end
            s.vm.post_up_message = "Node #{node_name} up and running. You can access the node with 'vagrant ssh #{node_name}'}"
        end
    end
end
# EOF
